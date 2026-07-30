import type { EvidenceFile } from "../lib/evidenceRules";

export function uploadEvidence(
  conversationId: string,
  files: File[],
  onProgress: (fraction: number) => void,
): Promise<EvidenceFile[]> {
  const form = new FormData();
  form.append("conversationId", conversationId);
  for (const file of files) form.append("files", file);

  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    request.open("POST", "/api/evidence/upload");
    request.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable) onProgress(event.loaded / event.total);
    });
    request.addEventListener("load", () => {
      let payload: { files?: EvidenceFile[]; errors?: string[] };
      try {
        payload = JSON.parse(request.responseText);
      } catch {
        reject(new Error("The upload response could not be read."));
        return;
      }
      if (request.status >= 200 && request.status < 300 && payload.files) {
        resolve(payload.files);
        return;
      }
      reject(new Error(payload.errors?.join(" ") ?? "The upload failed."));
    });
    request.addEventListener("error", () => reject(new Error("The upload failed.")));
    request.addEventListener("abort", () => reject(new Error("The upload was cancelled.")));
    request.send(form);
  });
}
