"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { uploadEvidence } from "../api/evidenceClient";
import { categorize, validateSelection, type EvidenceFile } from "../lib/evidenceRules";

export type EvidenceSelection = { file: File; url: string };

export function useEvidenceUpload(conversationId: string | undefined) {
  const [items, setItems] = useState<EvidenceSelection[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const itemsRef = useRef<EvidenceSelection[]>([]);

  useEffect(() => {
    return () => {
      for (const item of itemsRef.current) URL.revokeObjectURL(item.url);
    };
  }, []);

  const commit = useCallback((next: EvidenceSelection[]) => {
    itemsRef.current = next;
    setItems(next);
  }, []);

  const add = useCallback(
    (incoming: File[]) => {
      const { accepted, errors: rejected } = validateSelection(
        itemsRef.current.map((item) => item.file),
        incoming,
      );
      setErrors(rejected);
      if (accepted.length === 0) return;
      const added = accepted.map((file) => ({ file, url: URL.createObjectURL(file) }));
      commit([...itemsRef.current, ...added]);
    },
    [commit],
  );

  const remove = useCallback(
    (target: File) => {
      const match = itemsRef.current.find((item) => item.file === target);
      if (match) URL.revokeObjectURL(match.url);
      commit(itemsRef.current.filter((item) => item.file !== target));
      setErrors([]);
    },
    [commit],
  );

  const submit = useCallback(async (): Promise<EvidenceFile[] | null> => {
    const files = itemsRef.current.map((item) => item.file);
    if (!conversationId || files.length === 0) return null;
    setUploading(true);
    setProgress(0);
    setErrors([]);
    try {
      return await uploadEvidence(conversationId, files, setProgress);
    } catch (error) {
      setErrors([error instanceof Error ? error.message : "The upload failed."]);
      return null;
    } finally {
      setUploading(false);
    }
  }, [conversationId]);

  const imageCount = items.filter((item) => categorize(item.file.name, item.file.type) === "image").length;
  const videoCount = items.filter((item) => categorize(item.file.name, item.file.type) === "video").length;

  return { items, errors, progress, uploading, imageCount, videoCount, add, remove, submit };
}
