import { mkdir, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { getSession } from "@/features/auth";
import {
  MAX_IMAGES,
  MAX_IMAGE_BYTES,
  MAX_VIDEO_BYTES,
  categorizeByExtension,
  safeFilename,
  storageName,
  validateSelection,
  type EvidenceFile,
} from "@/features/chat";

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

const MAX_REQUEST_BYTES = MAX_VIDEO_BYTES + MAX_IMAGES * MAX_IMAGE_BYTES;

function evidenceRoot(): string {
  return process.env.EVIDENCE_TMP_DIR ?? path.join(process.cwd(), "tmp");
}

export async function POST(request: Request) {
  const session = await getSession();
  if (!session) return Response.json({ errors: ["Not signed in."] }, { status: 401 });

  const declaredLength = Number(request.headers.get("content-length") ?? 0);
  if (declaredLength > MAX_REQUEST_BYTES) {
    return Response.json({ errors: ["That upload is too large."] }, { status: 413 });
  }

  const form = await request.formData();
  const conversationId = String(form.get("conversationId") ?? "");
  if (!UUID_PATTERN.test(conversationId)) {
    return Response.json({ errors: ["A valid conversation is required."] }, { status: 400 });
  }

  const incoming = form.getAll("files").filter((entry): entry is File => entry instanceof File);
  if (incoming.length === 0) {
    return Response.json({ errors: ["No files were provided."] }, { status: 400 });
  }

  const directory = path.join(evidenceRoot(), safeFilename(session.sub), conversationId);
  await mkdir(directory, { recursive: true });

  const alreadyStored = await readdir(directory).catch(() => [] as string[]);
  const replacing = new Set(incoming.map((entry) => storageName(entry.name, entry.type)));
  const { accepted, errors } = validateSelection(
    alreadyStored.filter((name) => !replacing.has(name)).map((name) => ({ name })),
    incoming,
  );
  if (errors.length > 0) return Response.json({ errors }, { status: 400 });

  const stored: EvidenceFile[] = [];
  for (const entry of accepted) {
    const name = storageName(entry.name, entry.type);
    await writeFile(path.join(directory, name), Buffer.from(await entry.arrayBuffer()));
    stored.push({ name, category: categorizeByExtension(name) as "image" | "video", size: entry.size });
  }

  return Response.json({ files: stored });
}
