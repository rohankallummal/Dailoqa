import { readFileSync, readdirSync, statSync } from "fs";
import { join, basename } from "path";

const files = [];
(function walk(d) {
  for (const e of readdirSync(d)) {
    const p = join(d, e);
    if (statSync(p).isDirectory()) walk(p);
    else if (/\.(ts|tsx)$/.test(p)) files.push(p.split("\\").join("/"));
  }
})("src");

const text = new Map(files.map((f) => [f, readFileSync(f, "utf8")]));
const isEntry = (f) =>
  /\/(page|layout|route|not-found|error|loading|template|default)\.tsx?$/.test(f) ||
  /next-env\.d\.ts$/.test(f);

const exportsOf = new Map();
for (const [f, src] of text) {
  const names = new Set();
  const re =
    /export\s+(?:async\s+)?(?:function|const|let|var|class|type|interface|enum)\s+([A-Za-z0-9_$]+)/g;
  let m;
  while ((m = re.exec(src))) names.add(m[1]);
  const re2 = /export\s*\{([^}]+)\}/g;
  while ((m = re2.exec(src)))
    for (const part of m[1].split(",")) {
      const n = part.trim().split(/\s+as\s+/).pop().trim();
      if (n) names.add(n);
    }
  exportsOf.set(f, names);
}

console.log("=== FILES NEVER IMPORTED (non-entry) ===");
for (const f of files) {
  if (isEntry(f)) continue;
  const stem = basename(f).replace(/\.tsx?$/, "");
  let referenced = false;
  for (const [g, src] of text) {
    if (g === f) continue;
    if (new RegExp("from\\s+[\"'`][^\"'`]*\\b" + stem + "\\b").test(src)) {
      referenced = true;
      break;
    }
  }
  if (!referenced) console.log("  " + f);
}

console.log("\n=== EXPORTS WITH NO EXTERNAL REFERENCE ===");
for (const [f, names] of exportsOf) {
  for (const n of names) {
    let count = 0;
    for (const [g, src] of text) {
      if (g === f) continue;
      const hits = src.match(new RegExp("\\b" + n.replace(/\$/g, "\\$") + "\\b", "g"));
      if (hits) count += hits.length;
    }
    if (count === 0) console.log(`  ${f} :: ${n}`);
  }
}
