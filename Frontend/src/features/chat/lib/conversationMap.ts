export type MessageAnchor = {
  id: string;
  preview: string;
  top: number;
};

export type NavigatorMarker = {
  key: string;
  active: boolean;
};

export const MAX_MARKERS = 20;
export const MARKER_HEIGHT = 3;
export const MARKER_WIDTH = 26;

const EMPTY_PREVIEW = "Empty message";
const BLOCK_PREFIX = /^\s*(?:[-*+]\s+|\d+\.\s+|>\s?|#{1,6}\s+)+/;
const INLINE_MARKS = /[`*_~]+/g;

export function derivePreview(content: string) {
  for (const raw of content.split("\n")) {
    const line = raw.replace(BLOCK_PREFIX, "").replace(INLINE_MARKS, "").trim();
    if (line.length > 2) return line;
  }
  return content.trim() || EMPTY_PREVIEW;
}

export function resolveActiveId(anchors: MessageAnchor[], readingLine: number, atBottom: boolean) {
  if (anchors.length === 0) return null;
  if (atBottom) return anchors[anchors.length - 1].id;
  let active = anchors[0].id;
  for (const anchor of anchors) {
    if (anchor.top > readingLine) break;
    active = anchor.id;
  }
  return active;
}

export function buildMarkers({
  anchors,
  activeId,
}: {
  anchors: MessageAnchor[];
  activeId: string | null;
}): NavigatorMarker[] {
  const count = Math.min(anchors.length, MAX_MARKERS);
  if (count === 0) return [];

  const activeIndex = anchors.findIndex((anchor) => anchor.id === activeId);
  const activeMarker =
    activeIndex < 0 ? -1 : Math.floor((activeIndex * count) / anchors.length);

  return Array.from({ length: count }, (_, index) => ({
    key: count === anchors.length ? anchors[index].id : `band-${index}`,
    active: index === activeMarker,
  }));
}
