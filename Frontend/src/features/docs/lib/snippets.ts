import { readdir } from "node:fs/promises";
import path from "node:path";
import { compileSource, langdocsRoot, readDoc, type MdxComponent } from "./compileMdx";
import { splitFrontmatter } from "./frontmatter";

const SNIPPETS_DIR = "snippets";

const nameOverrides: Record<string, string> = {
  "snippets/chat-model-tabs.mdx": "ChatModelTabsPy",
  "snippets/chat-model-tabs-js.mdx": "ChatModelTabsJS",
  "snippets/sandboxes-basic-tabs-py.mdx": "SandboxesBasicTabsPy",
  "snippets/skills-usage-tabs-js.mdx": "SkillsUsageTabsJs",
  "snippets/skills-usage-tabs-py.mdx": "SkillsUsageTabsPy",
  "snippets/code-samples/deepagents-sandbox-lifecycle-factory-assistant-js.mdx":
    "DeepagentsSandboxLifecycleFactoryAssistantTs",
  "snippets/code-samples/deepagents-sandbox-lifecycle-factory-thread-js.mdx":
    "DeepagentsSandboxLifecycleFactoryThreadTs",
};

export function componentName(relPath: string): string {
  return (
    nameOverrides[relPath] ??
    path
      .basename(relPath, ".mdx")
      .split("-")
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join("")
  );
}

export async function snippetPaths(): Promise<string[]> {
  const entries = await readdir(path.join(langdocsRoot, SNIPPETS_DIR), { recursive: true });
  return entries
    .map((entry) => `${SNIPPETS_DIR}/${entry.split(path.sep).join("/")}`)
    .filter((entry) => entry.endsWith(".mdx"))
    .sort();
}

let cache: Record<string, MdxComponent> | null = null;

export async function compileSnippets(): Promise<Record<string, MdxComponent>> {
  if (cache) return cache;
  const paths = await snippetPaths();
  const entries = await Promise.all(
    paths.map(async (relPath) => {
      const { body } = splitFrontmatter(await readDoc(relPath));
      return [componentName(relPath), await compileSource(body)] as const;
    }),
  );
  cache = Object.fromEntries(entries);
  return cache;
}
