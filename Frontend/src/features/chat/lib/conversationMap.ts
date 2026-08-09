import type { Message } from "./messageReducer";

export type MessageAnchor = {
  id: string;
  role: Message["role"];
  preview: string;
  top: number;
};

export type NavigatorMarker = {
  key: string;
  top: number;
  active: boolean;
};

export const MAX_MARKERS = 20;
export const MARKER_HEIGHT = 2;
export const MARKER_WIDTH = 14;

const MARKER_PITCH = MARKER_HEIGHT + 4;
const EMPTY_PREVIEW = "Empty message";
const BLOCK_PREFIX = /^\s*(?:[-*+]\s+|\d+\.\s+|>\s?|#{1,6}\s+)+/;
const INLINE_MARKS = /[`*_~]+/g;

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

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

function separate(markers: NavigatorMarker[], span: number) {
  for (let index = 1; index < markers.length; index += 1) {
    markers[index].top = Math.max(markers[index].top, markers[index - 1].top + MARKER_PITCH);
  }
  for (let index = markers.length - 1; index >= 0; index -= 1) {
    const ceiling = index === markers.length - 1 ? span : markers[index + 1].top - MARKER_PITCH;
    markers[index].top = clamp(markers[index].top, 0, Math.max(0, ceiling));
  }
  return markers;
}

export function buildMarkers({
  anchors,
  scrollHeight,
  railHeight,
  activeId,
}: {
  anchors: MessageAnchor[];
  scrollHeight: number;
  railHeight: number;
  activeId: string | null;
}): NavigatorMarker[] {
  if (anchors.length === 0) return [];

  const span = Math.max(0, railHeight - MARKER_HEIGHT);
  const height = Math.max(1, scrollHeight);
  const project = (top: number) => clamp(Math.round((top / height) * span), 0, span);

  if (anchors.length <= MAX_MARKERS) {
    return separate(
      anchors.map((anchor) => ({
        key: anchor.id,
        top: project(anchor.top),
        active: anchor.id === activeId,
      })),
      span,
    );
  }

  const band = height / MAX_MARKERS;
  const activeAnchor = anchors.find((anchor) => anchor.id === activeId);
  const activeBand = activeAnchor ? clamp(Math.floor(activeAnchor.top / band), 0, MAX_MARKERS - 1) : 0;

  return Array.from({ length: MAX_MARKERS }, (_, index) => ({
    key: `band-${index}`,
    top: project(index * band),
    active: index === activeBand,
  }));
}
