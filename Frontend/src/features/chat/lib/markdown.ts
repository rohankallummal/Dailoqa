type HastNode = {
  type?: string;
  tagName?: string;
  value?: string;
  properties?: { className?: unknown };
  children?: HastNode[];
};

const FENCE = /^\s*```/;
const LANGUAGE = /^language-(.+)$/;

export function balanceCodeFences(content: string): string {
  const opened = content.split("\n").filter((line) => FENCE.test(line)).length;
  return opened % 2 === 0 ? content : `${content}\n\`\`\``;
}

export function nodeText(node: HastNode | undefined): string {
  if (!node) return "";
  if (node.type === "text") return node.value ?? "";
  return (node.children ?? []).map(nodeText).join("");
}

export function codeLanguage(node: HastNode | undefined): string {
  const code = (node?.children ?? []).find((child) => child.tagName === "code");
  const names = code?.properties?.className;
  if (!Array.isArray(names)) return "";
  for (const name of names) {
    const matched = LANGUAGE.exec(String(name));
    if (matched) return matched[1];
  }
  return "";
}
