import { SKIP, visit } from "unist-util-visit";
import GithubSlugger from "github-slugger";

export type TocItem = { depth: 2 | 3; text: string; slug: string };

type UnistNode = {
  type: string;
  name?: string;
  value?: string;
  lang?: string | null;
  meta?: string | null;
  depth?: number;
  attributes?: unknown[];
  children?: UnistNode[];
  data?: Record<string, unknown>;
};

type SourceFile = { value?: unknown };

type SourceSpan = { start?: { offset?: number }; end?: { offset?: number } };

function jsxAttribute(name: string, value: string) {
  return { type: "mdxJsxAttribute", name, value };
}

function collectText(node: UnistNode): string {
  if (node.type === "text" || node.type === "inlineCode") {
    return node.value ?? "";
  }
  if (Array.isArray(node.children)) {
    return node.children.map(collectText).join("");
  }
  return "";
}

export function remarkStripEsm() {
  return (tree: UnistNode) => {
    if (Array.isArray(tree.children)) {
      tree.children = tree.children.filter((node) => node.type !== "mdxjsEsm");
    }
  };
}

const commentExpression = /^\s*\/\*[\s\S]*\*\/\s*$/;

export function remarkLiteralExpressions() {
  return (tree: UnistNode) => {
    visit(tree, (node: UnistNode, index, parent: UnistNode | undefined) => {
      if (
        node.type !== "mdxTextExpression" &&
        node.type !== "mdxFlowExpression"
      ) {
        return;
      }
      if (!parent?.children || typeof index !== "number") return;

      if (commentExpression.test(node.value ?? "")) {
        parent.children.splice(index, 1);
        return [SKIP, index];
      }

      const text: UnistNode = { type: "text", value: `{${node.value ?? ""}}` };
      parent.children[index] =
        node.type === "mdxFlowExpression"
          ? { type: "paragraph", children: [text] }
          : text;
    });
  };
}

export function remarkApiRef() {
  return (tree: UnistNode) => {
    visit(tree, (node: UnistNode, index, parent: UnistNode | undefined) => {
      if (node.type !== "inlineCode") return;
      if (!parent || typeof index !== "number") return;
      const previous = parent.children?.[index - 1];
      const next = parent.children?.[index + 1];
      if (
        previous?.type === "text" &&
        previous.value?.endsWith("@[") &&
        next?.type === "text" &&
        next.value?.startsWith("]")
      ) {
        previous.value = previous.value.slice(0, -2);
        next.value = next.value.slice(1);
      }
    });
  };
}

export function remarkLangBlocks() {
  return (tree: UnistNode) => {
    visit(tree, (node: UnistNode) => {
      if (node.type !== "containerDirective") return;
      if (node.name !== "python" && node.name !== "js") return;
      const lang = node.name;
      node.type = "mdxJsxFlowElement";
      node.name = "LangBlock";
      node.attributes = [jsxAttribute("lang", lang)];
    });
  };
}

const jsxElementTypes = new Set(["mdxJsxFlowElement", "mdxJsxTextElement"]);
const droppedJsxAttributes = new Set(["noZoom"]);

export function remarkStripJsxAttributes() {
  return (tree: UnistNode) => {
    visit(tree, (node: UnistNode) => {
      if (!jsxElementTypes.has(node.type)) return;
      if (!Array.isArray(node.attributes)) return;
      const name = node.name ?? "";
      if (name !== name.toLowerCase()) return;

      node.attributes = node.attributes.filter((attribute) => {
        const attributeName = (attribute as { name?: string })?.name;
        return !attributeName || !droppedJsxAttributes.has(attributeName);
      });
    });
  };
}

const directiveTypes = new Set([
  "textDirective",
  "leafDirective",
  "containerDirective",
]);

export function remarkLiteralDirectives() {
  return (tree: UnistNode, file: SourceFile) => {
    const source = typeof file?.value === "string" ? file.value : "";
    visit(tree, (node: UnistNode, index, parent: UnistNode | undefined) => {
      if (!directiveTypes.has(node.type)) return;
      if (!parent?.children || typeof index !== "number") return;

      const span = (node as { position?: SourceSpan }).position;
      const start = span?.start?.offset;
      const end = span?.end?.offset;
      const literal =
        source && typeof start === "number" && typeof end === "number"
          ? source.slice(start, end)
          : `:${node.name ?? ""}`;

      parent.children[index] = { type: "text", value: literal };
      return [SKIP, index];
    });
  };
}

export function remarkCodeBlocks() {
  return (tree: UnistNode) => {
    visit(tree, (node: UnistNode) => {
      if (node.type !== "code") return;
      const meta = (node.meta ?? "").trim();
      const attributes = [
        jsxAttribute("language", node.lang ?? ""),
        jsxAttribute("title", meta),
        jsxAttribute("code", node.value ?? ""),
      ];
      node.type = "mdxJsxFlowElement";
      node.name = "CodeBlock";
      node.attributes = attributes;
      node.children = [];
      delete node.value;
      delete node.lang;
      delete node.meta;
    });
  };
}

export function remarkCollectToc(out: TocItem[]) {
  return () => (tree: UnistNode) => {
    const slugger = new GithubSlugger();
    visit(tree, (node: UnistNode) => {
      if (node.type !== "heading") return;
      if (node.depth !== 2 && node.depth !== 3) return;
      const text = (node.children ?? []).map(collectText).join("").trim();
      if (!text) return;
      const slug = slugger.slug(text);
      node.data = node.data ?? {};
      const hProperties = (node.data.hProperties as Record<string, unknown>) ?? {};
      node.data.hProperties = { ...hProperties, id: slug };
      out.push({ depth: node.depth as 2 | 3, text, slug });
    });
  };
}
