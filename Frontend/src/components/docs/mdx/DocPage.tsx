import { renderPage } from "./compileMdx";
import { getMdxComponents } from "./mdxComponents";
import { LanguageProvider } from "./LanguageProvider";
import { LanguageToggle } from "./LanguageToggle";
import { TableOfContents } from "./TableOfContents";

export async function DocPage({ relPath }: { relPath: string }) {
  const [{ title, description, toc, Content }, components] = await Promise.all([
    renderPage(relPath),
    getMdxComponents(),
  ]);

  const storageKey = `${relPath.split("/")[0]}Lang`;

  return (
    <LanguageProvider storageKey={storageKey}>
      <div className="mx-auto flex w-full max-w-6xl gap-10 px-8 py-10">
        <div className="min-w-0 flex-1">
          <header>
            {title ? (
              <h1 className="text-3xl font-semibold tracking-tight text-ink">
                {title}
              </h1>
            ) : null}
            {description ? (
              <p className="mt-3 text-base leading-relaxed text-ink-soft">
                {description}
              </p>
            ) : null}
            <div className="mt-6">
              <LanguageToggle />
            </div>
          </header>
          <article className="docArticle mt-8">
            <Content components={components} />
          </article>
        </div>
        <aside className="hidden w-56 flex-shrink-0 xl:block">
          <TableOfContents items={toc} />
        </aside>
      </div>
    </LanguageProvider>
  );
}
