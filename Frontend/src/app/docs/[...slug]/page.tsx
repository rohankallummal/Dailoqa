import { notFound } from "next/navigation";
import { DocPage, docsPageSources } from "@/features/docs";

export const dynamicParams = false;

export function generateStaticParams() {
  return Object.keys(docsPageSources).map((href) => ({ slug: href.split("/").slice(2) }));
}

export default async function Page({ params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  const relPath = docsPageSources[`/docs/${slug.join("/")}`];
  if (!relPath) notFound();
  return <DocPage relPath={relPath} />;
}
