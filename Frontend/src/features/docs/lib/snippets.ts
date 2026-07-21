import { compileSource, readDoc, type MdxComponent } from "./compileMdx";
import { splitFrontmatter } from "./frontmatter";

const snippetFiles: Record<string, string> = {
  OverviewQuickstartPy: "snippets/code-samples/overview-quickstart-py.mdx",
  OverviewQuickstartJs: "snippets/code-samples/overview-quickstart-js.mdx",
  OverviewToolsPy: "snippets/code-samples/overview-tools-py.mdx",
  OverviewExcludedToolsPy: "snippets/code-samples/overview-excluded-tools-py.mdx",
};

let cache: Record<string, MdxComponent> | null = null;

export async function compileSnippets(): Promise<Record<string, MdxComponent>> {
  if (cache) return cache;
  const entries = await Promise.all(
    Object.entries(snippetFiles).map(async ([name, relPath]) => {
      const raw = await readDoc(relPath);
      const { body } = splitFrontmatter(raw);
      const Component = await compileSource(body);
      return [name, Component] as const;
    }),
  );
  cache = Object.fromEntries(entries);
  return cache;
}
