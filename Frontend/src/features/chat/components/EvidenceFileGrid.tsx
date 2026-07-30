"use client";

import { X } from "lucide-react";
import { categorize, formatSize, storageName } from "../lib/evidenceRules";
import type { EvidenceSelection } from "../hooks/useEvidenceUpload";

export function EvidenceFileGrid({
  items,
  onRemove,
}: {
  items: EvidenceSelection[];
  onRemove: (file: File) => void;
}) {
  if (items.length === 0) return null;

  return (
    <div className="grid grid-cols-3 gap-2 @sm:grid-cols-5">
      {items.map(({ file, url }) => {
        const isVideo = categorize(file.name, file.type) === "video";
        return (
          <div
            key={storageName(file.name, file.type)}
            className="relative aspect-square overflow-hidden rounded-lg border border-line bg-page"
          >
            {isVideo ? (
              <video src={url} muted className="h-full w-full object-cover" />
            ) : (
              <span
                role="img"
                aria-label={file.name}
                style={{ backgroundImage: `url(${url})` }}
                className="block h-full w-full bg-cover bg-center"
              />
            )}
            <span className="absolute left-1 top-1 rounded bg-ink/70 px-1 py-0.5 text-[9px] font-semibold uppercase tracking-wide text-white">
              {isVideo ? "Video" : "Img"}
            </span>
            <button
              type="button"
              onClick={() => onRemove(file)}
              aria-label={`Remove ${file.name}`}
              className="absolute right-1 top-1 flex h-5 w-5 items-center justify-center rounded bg-ink/70 text-white transition-colors duration-200 hover:bg-ink"
            >
              <X className="h-3 w-3" strokeWidth={2.5} />
            </button>
            <span className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-ink/80 to-transparent px-1.5 pb-1 pt-3 text-[10px] text-white">
              {formatSize(file.size)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
