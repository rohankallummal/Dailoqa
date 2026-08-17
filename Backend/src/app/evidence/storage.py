"""Filesystem storage, validation, and cleanup for bug-report evidence."""

import re
import shutil
import time
from pathlib import Path

from app.config import get_settings

IMAGE_EXTENSIONS = frozenset(
    {"png", "jpg", "jpeg", "gif", "webp", "bmp", "heic", "heif", "avif", "tiff"}
)
VIDEO_EXTENSIONS = frozenset({"mp4", "mov", "webm", "avi", "mkv", "m4v", "ogv"})

MAX_IMAGES = 5
MAX_VIDEOS = 1
MAX_VIDEO_BYTES = 50 * 1024 * 1024
MAX_IMAGE_BYTES = 10 * 1024 * 1024
ORPHAN_AGE_SECONDS = 24 * 60 * 60

_UUID_PATTERN = re.compile(
    r"\A[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\Z"
)
_UNSAFE_CHARACTERS = re.compile(r"[^A-Za-z0-9._-]")


def categorize(filename: str) -> str:
    """Classify a filename as image, video, or other by its extension."""
    _, separator, extension = filename.rpartition(".")
    if not separator:
        return "other"
    extension = extension.lower()
    if extension in IMAGE_EXTENSIONS:
        return "image"
    if extension in VIDEO_EXTENSIONS:
        return "video"
    return "other"


def safe_filename(name: str) -> str:
    """Reduce an untrusted name to a bare, filesystem-safe basename."""
    basename = name.replace("\\", "/").rpartition("/")[2]
    cleaned = _UNSAFE_CHARACTERS.sub("_", basename).strip(".")
    return cleaned or "file"


def evidence_dir(user_sub: str, conversation_id: str) -> Path:
    """Return the directory holding one conversation's evidence.

    Raises ValueError when conversation_id is not a UUID, so an untrusted value can
    never be used as a path segment.
    """
    if not _UUID_PATTERN.match(conversation_id):
        raise ValueError(f"invalid conversation id: {conversation_id}")
    return Path(get_settings().evidence_root) / safe_filename(user_sub) / conversation_id


def _size_limit_error(name: str, size: int) -> str | None:
    """Return a size-limit message for one file, or None when it fits."""
    category = categorize(name)
    if category == "video" and size >= MAX_VIDEO_BYTES:
        return f"{name} is larger than 50 MB."
    if category == "image" and size > MAX_IMAGE_BYTES:
        return f"{name} is larger than 10 MB."
    return None


def normalize_manifest(user_sub: str, conversation_id: str, manifest: list[dict]) -> list[dict]:
    """Return the manifest rebuilt from the files actually on disk.

    The name is what the worker later joins onto the evidence directory to find the file to
    upload, so it is the sanitised one validate_manifest checked rather than whatever the
    client sent. Category and size are re-derived from the stored file for the same reason:
    the manifest is persisted into the job payload, and a client should not be able to write
    a media type or a size there that the file on disk contradicts. Client-supplied fields
    beyond these three are dropped rather than carried into the payload.
    """
    directory = evidence_dir(user_sub, conversation_id)
    normalized = []
    for entry in manifest:
        name = safe_filename(entry["name"])
        path = directory / name
        normalized.append(
            {
                "name": name,
                "category": categorize(name),
                "size": path.stat().st_size if path.is_file() else 0,
            }
        )
    return normalized


def validate_manifest(user_sub: str, conversation_id: str, manifest: list[dict]) -> list[str]:
    """Check a client manifest against the files actually on disk.

    Sizes are read from disk rather than taken from the manifest, so a client cannot
    declare a small size for a large file. Returns one message per problem; an empty
    list means the manifest is acceptable.
    """
    try:
        directory = evidence_dir(user_sub, conversation_id)
    except ValueError as error:
        return [str(error)]

    errors: list[str] = []
    images = 0
    videos = 0
    for entry in manifest:
        name = safe_filename(entry["name"])
        category = categorize(name)
        if category == "other":
            errors.append(f"{name} is not a supported image or video type.")
            continue
        path = directory / name
        if not path.is_file():
            errors.append(f"{name} was not found in storage.")
            continue
        size_error = _size_limit_error(name, path.stat().st_size)
        if size_error:
            errors.append(size_error)
            continue
        if category == "image":
            images += 1
        else:
            videos += 1

    if images > MAX_IMAGES:
        errors.append(f"Only {MAX_IMAGES} images may be attached.")
    if videos > MAX_VIDEOS:
        errors.append(f"Only {MAX_VIDEOS} video may be attached.")
    return errors


def _prune_if_empty(directory: Path) -> None:
    """Remove a directory only when it holds nothing, ignoring any failure.

    rmdir refuses a non-empty directory, so a concurrent report for the same user is
    left untouched rather than raced away.
    """
    try:
        directory.rmdir()
    except OSError:
        return


def delete_dir(user_sub: str, conversation_id: str) -> None:
    """Remove a conversation's evidence directory, never raising.

    Prunes the user directory too once its last conversation is gone, so the evidence
    root does not accumulate one empty folder per reporter forever.
    """
    try:
        directory = evidence_dir(user_sub, conversation_id)
    except ValueError:
        return
    shutil.rmtree(directory, ignore_errors=True)
    _prune_if_empty(directory.parent)


def sweep_orphans(
    max_age_seconds: int = ORPHAN_AGE_SECONDS,
    keep_conversation_ids: frozenset[str] = frozenset(),
) -> int:
    """Delete conversation directories older than max_age_seconds; return how many.

    A directory whose conversation id is in keep_conversation_ids is left alone however
    old it is. Age alone is not evidence of abandonment: a report can sit at its
    confirmation prompt overnight and still be resumable, and a job can wait in the queue
    while the worker is down. Sweeping either would file the ticket with its screenshots
    already deleted, and nothing re-uploads them.
    """
    root = Path(get_settings().evidence_root)
    if not root.is_dir():
        return 0
    cutoff = time.time() - max_age_seconds
    removed = 0
    for user_directory in root.iterdir():
        if not user_directory.is_dir():
            continue
        for conversation_directory in user_directory.iterdir():
            if not conversation_directory.is_dir():
                continue
            if conversation_directory.name in keep_conversation_ids:
                continue
            if conversation_directory.stat().st_mtime < cutoff:
                shutil.rmtree(conversation_directory, ignore_errors=True)
                removed += 1
        _prune_if_empty(user_directory)
    return removed
