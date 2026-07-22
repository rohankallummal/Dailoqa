import { createCipheriv, createDecipheriv, randomBytes } from "node:crypto";
import { getEncryptionKey } from "./env";

function key(): Buffer {
  const decoded = Buffer.from(getEncryptionKey(), "base64");
  if (decoded.length !== 32) {
    throw new Error("ENCRYPTION_KEY must decode to 32 bytes (base64)");
  }
  return decoded;
}

export function encryptSecret(plaintext: string): string {
  const iv = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", key(), iv);
  const ciphertext = Buffer.concat([cipher.update(plaintext, "utf8"), cipher.final()]);
  const authTag = cipher.getAuthTag();
  return [
    iv.toString("base64"),
    authTag.toString("base64"),
    ciphertext.toString("base64"),
  ].join(":");
}

export function decryptSecret(payload: string): string {
  const [ivB64, tagB64, ctB64] = payload.split(":");
  const decipher = createDecipheriv("aes-256-gcm", key(), Buffer.from(ivB64, "base64"));
  decipher.setAuthTag(Buffer.from(tagB64, "base64"));
  return Buffer.concat([
    decipher.update(Buffer.from(ctB64, "base64")),
    decipher.final(),
  ]).toString("utf8");
}
