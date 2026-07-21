import { readFile } from "node:fs/promises";
import path from "node:path";
import { compile, run } from "@mdx-js/mdx";
import * as jsxRuntime from "react/jsx-runtime";
import remarkGfm from "remark-gfm";
import remarkDirective from "remark-directive";
import type { ComponentType } from "react";
import { splitFrontmatter } from "./frontmatter";
import {
  remarkApiRef,
  remarkCodeBlocks,
  remarkCollectToc,
  remarkLangBlocks,
  remarkStripEsm,
  type TocItem,
} from "./plugins";

export type MdxComponent = ComponentType<{ components?: Record<string, unknown> }>;

export type RenderedPage = {
  title: string;
  description: string;
  toc: TocItem[];
  Content: MdxComponent;
};

const runtime = {
  Fragment: jsxRuntime.Fragment,
  jsx: jsxRuntime.jsx,
  jsxs: jsxRuntime.jsxs,
};

const langdocsRoot = path.join(
  process.cwd(),
  "src",
  "features",
  "docs",
  "content",
  "langdocs",
);

export async function compileSource(
  source: string,
  collectToc?: TocItem[],
): Promise<MdxComponent> {
  const remarkPlugins = [
    remarkGfm,
    remarkDirective,
    remarkStripEsm,
    remarkApiRef,
    remarkLangBlocks,
    remarkCodeBlocks,
    ...(collectToc ? [remarkCollectToc(collectToc)] : []),
  ];

  const compiled = await compile(source, {
    outputFormat: "function-body",
    remarkPlugins,
  });

  const mod = await run(String(compiled), runtime);
  return mod.default as MdxComponent;
}

export async function readDoc(relPath: string): Promise<string> {
  return readFile(path.join(langdocsRoot, relPath), "utf8");
}

const pageCache = new Map<string, Promise<RenderedPage>>();

async function buildPage(relPath: string): Promise<RenderedPage> {
  const raw = await readDoc(relPath);
  const { title, description, body } = splitFrontmatter(raw);
  const toc: TocItem[] = [];
  const Content = await compileSource(body, toc);
  return { title, description, toc, Content };
}

export function renderPage(relPath: string): Promise<RenderedPage> {
  if (process.env.NODE_ENV !== "production") {
    return buildPage(relPath);
  }
  const cached = pageCache.get(relPath);
  if (cached) return cached;
  const built = buildPage(relPath);
  pageCache.set(relPath, built);
  return built;
}
