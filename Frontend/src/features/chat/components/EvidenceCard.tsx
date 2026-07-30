"use client";

import { useState } from "react";
import { AlertCircle, Paperclip, Plus } from "lucide-react";
import { EvidenceDropzone } from "./EvidenceDropzone";
import { EvidenceFileGrid } from "./EvidenceFileGrid";
import { useEvidenceUpload } from "../hooks/useEvidenceUpload";
import { MAX_IMAGES, MAX_VIDEOS, type EvidenceFile } from "../lib/evidenceRules";

const CANCEL_TEXT = "I don't have any evidence to provide.";

function describe(files: EvidenceFile[]): string {
  const images = files.filter((file) => file.category === "image").length;
  const videos = files.filter((file) => file.category === "video").length;
  const parts = [
    images > 0 ? `${images} image${images > 1 ? "s" : ""}` : "",
    videos > 0 ? `${videos} video` : "",
  ].filter(Boolean);
  return `Attached ${parts.join(" and ")}.`;
}

export function EvidenceCard({
  conversationId,
  onSubmit,
  onCancel,
}: {
  conversationId: string | undefined;
  onSubmit: (text: string, evidence: EvidenceFile[]) => void;
  onCancel: (text: string) => void;
}) {
  const [picking, setPicking] = useState(false);
  const { items, errors, progress, uploading, imageCount, videoCount, add, remove, submit } =
    useEvidenceUpload(conversationId);

  const handleSubmit = async () => {
    const uploaded = await submit();
    if (uploaded) onSubmit(describe(uploaded), uploaded);
  };

  return (
    <div className="@container w-full flex-shrink-0 p-3">
      <div className="rounded-xl border border-line bg-white p-3.5">
        <div className="mb-2 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-accent">
          <Paperclip className="h-3.5 w-3.5" strokeWidth={2} />
          Evidence
        </div>

        <p className="mb-3 text-sm leading-relaxed text-ink">
          Attach screenshots or a screen recording that show the problem.
        </p>

        <div className="mb-3 rounded-lg bg-page px-3 py-2 text-xs leading-relaxed text-ink-soft">
          Images and video only. Up to <span className="font-semibold text-ink">{MAX_IMAGES} images</span> and{" "}
          <span className="font-semibold text-ink">{MAX_VIDEOS} video</span> under{" "}
          <span className="font-semibold text-ink">50 MB</span>.
        </div>

        {picking && (
          <div className="flex flex-col gap-3">
            <EvidenceDropzone onAdd={add} />

            <div className="flex gap-2 text-xs">
              <span className="flex flex-1 items-center justify-between rounded-lg border border-line bg-page px-2.5 py-1.5">
                <span className="text-ink-muted">Images</span>
                <span className={imageCount >= MAX_IMAGES ? "font-semibold text-accent" : "font-semibold text-ink"}>
                  {imageCount} / {MAX_IMAGES}
                </span>
              </span>
              <span className="flex flex-1 items-center justify-between rounded-lg border border-line bg-page px-2.5 py-1.5">
                <span className="text-ink-muted">Video</span>
                <span className={videoCount >= MAX_VIDEOS ? "font-semibold text-accent" : "font-semibold text-ink"}>
                  {videoCount} / {MAX_VIDEOS}
                </span>
              </span>
            </div>

            {errors.length > 0 && (
              <div className="flex gap-2 rounded-lg border border-line bg-page px-3 py-2 text-xs text-ink-soft">
                <AlertCircle className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-accent" strokeWidth={2} />
                <ul className="flex flex-col gap-1">
                  {errors.map((message) => (
                    <li key={message}>{message}</li>
                  ))}
                </ul>
              </div>
            )}

            <EvidenceFileGrid items={items} onRemove={remove} />

            {uploading && (
              <div className="h-1 overflow-hidden rounded-full bg-page">
                <div
                  className="h-full rounded-full bg-accent transition-[width] duration-150"
                  style={{ width: `${Math.round(progress * 100)}%` }}
                />
              </div>
            )}
          </div>
        )}

        <div className="mt-3 flex gap-2">
          {picking ? (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={items.length === 0 || uploading}
              className="flex-1 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-40"
            >
              {uploading ? "Uploading…" : "Attach evidence"}
            </button>
          ) : (
            <button
              type="button"
              onClick={() => setPicking(true)}
              className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-opacity duration-200 hover:opacity-90"
            >
              <Plus className="h-4 w-4" strokeWidth={2} />
              Add evidence
            </button>
          )}
          <button
            type="button"
            onClick={() => onCancel(CANCEL_TEXT)}
            disabled={uploading}
            className="rounded-lg border border-line px-4 py-2 text-sm font-medium text-ink-soft transition-colors duration-200 hover:bg-hover hover:text-ink disabled:opacity-40"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
