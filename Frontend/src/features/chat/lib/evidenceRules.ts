export const IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "webp", "bmp", "heic", "heif", "avif", "tiff"];
export const VIDEO_EXTENSIONS = ["mp4", "mov", "webm", "avi", "mkv", "m4v", "ogv"];

export const MAX_IMAGES = 5;
export const MAX_VIDEOS = 1;
export const MAX_VIDEO_BYTES = 50 * 1024 * 1024;
export const MAX_IMAGE_BYTES = 10 * 1024 * 1024;

export type EvidenceCategory = "image" | "video" | "other";

export type EvidenceFile = { name: string; category: "image" | "video"; size: number };

const MIME_EXTENSIONS: Record<string, string> = {
  "image/png": "png",
  "image/jpeg": "jpg",
  "image/gif": "gif",
  "image/webp": "webp",
  "image/bmp": "bmp",
  "image/heic": "heic",
  "image/heif": "heif",
  "image/avif": "avif",
  "image/tiff": "tiff",
  "video/mp4": "mp4",
  "video/quicktime": "mov",
  "video/webm": "webm",
  "video/x-msvideo": "avi",
  "video/x-matroska": "mkv",
  "video/x-m4v": "m4v",
  "video/ogg": "ogv",
};

function extensionOf(name: string): string {
  const parts = name.split(".");
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : "";
}

export function categorizeByExtension(name: string): EvidenceCategory {
  const extension = extensionOf(name);
  if (IMAGE_EXTENSIONS.includes(extension)) return "image";
  if (VIDEO_EXTENSIONS.includes(extension)) return "video";
  return "other";
}

export function categorize(name: string, mimeType = ""): EvidenceCategory {
  const byExtension = categorizeByExtension(name);
  if (byExtension !== "other") return byExtension;
  const mime = mimeType.toLowerCase();
  if (mime.startsWith("image/")) return "image";
  if (mime.startsWith("video/")) return "video";
  return "other";
}

export function storageName(name: string, mimeType = ""): string {
  const base = safeFilename(name);
  if (categorizeByExtension(base) !== "other") return base;
  const extension = MIME_EXTENSIONS[mimeType.toLowerCase().split(";")[0].trim()];
  return extension ? `${base}.${extension}` : base;
}

export function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function safeFilename(name: string): string {
  const basename = name.replace(/\\/g, "/").split("/").pop() ?? "";
  const cleaned = basename.replace(/[^A-Za-z0-9._-]/g, "_").replace(/^\.+|\.+$/g, "");
  return cleaned || "file";
}

export type NamedFile = { name: string; type?: string };

export function validateSelection(
  existing: NamedFile[],
  incoming: File[],
): { accepted: File[]; errors: string[] } {
  const accepted: File[] = [];
  const errors: string[] = [];
  const taken = new Set(existing.map((item) => storageName(item.name, item.type ?? "")));
  let images = existing.filter((item) => categorize(item.name, item.type ?? "") === "image").length;
  let videos = existing.filter((item) => categorize(item.name, item.type ?? "") === "video").length;

  for (const candidate of incoming) {
    const category = categorize(candidate.name, candidate.type);
    if (category === "other") {
      errors.push(`${candidate.name} is not a supported image or video type.`);
      continue;
    }
    const stored = storageName(candidate.name, candidate.type);
    if (taken.has(stored)) {
      errors.push(`${candidate.name} is already attached.`);
      continue;
    }
    if (category === "image") {
      if (images >= MAX_IMAGES) {
        errors.push(`${candidate.name} exceeds the limit of ${MAX_IMAGES} images.`);
        continue;
      }
      if (candidate.size > MAX_IMAGE_BYTES) {
        errors.push(`${candidate.name} is larger than 10 MB.`);
        continue;
      }
      images += 1;
    } else {
      if (videos >= MAX_VIDEOS) {
        errors.push(`${candidate.name} exceeds the limit of ${MAX_VIDEOS} video.`);
        continue;
      }
      if (candidate.size >= MAX_VIDEO_BYTES) {
        errors.push(`${candidate.name} is larger than 50 MB.`);
        continue;
      }
      videos += 1;
    }
    taken.add(stored);
    accepted.push(candidate);
  }
  return { accepted, errors };
}
