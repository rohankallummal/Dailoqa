import type { ReactNode } from "react";
import { File as FileGlyph } from "lucide-react";
import { TreeFolder } from "./TreeFolder";

function TreeRoot({ children }: { children?: ReactNode }) {
  return (
    <div className="my-4 rounded-xl border border-line bg-white px-4 py-3 font-mono text-sm text-ink-soft">
      {children}
    </div>
  );
}

function TreeFile({ name }: { name?: string }) {
  return (
    <div className="flex items-center gap-1.5 py-0.5 pl-5">
      <FileGlyph className="h-3.5 w-3.5 flex-shrink-0 text-ink-muted" />
      {name}
    </div>
  );
}

export const Tree = Object.assign(TreeRoot, {
  File: TreeFile,
  Folder: TreeFolder,
});
