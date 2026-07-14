import { LanguageProvider } from "@/components/docs/mdx/LanguageProvider";
import { LanguageToggle } from "@/components/docs/mdx/LanguageToggle";
import { OverviewCards } from "@/components/docs/OverviewCards";

export default function Page() {
  return (
    <div className="mx-auto w-full max-w-6xl px-8 py-12">
      <h1 className="text-3xl font-semibold tracking-tight text-ink">Build</h1>
      <p className="mt-4 text-base leading-relaxed text-ink-soft">
        The dailoqa open source stack provides the building blocks you need to
        design, test, and ship agents.
      </p>

      <h2 className="mt-16 text-xl font-semibold tracking-tight text-ink">
        Choose your starting point
      </h2>
      <p className="mt-2 text-sm text-ink-soft">
        Deep Agents, LangChain, and LangGraph share the same stack, so choose
        based on how much control you need:
      </p>

      <LanguageProvider storageKey="overviewLang">
        <div className="mt-6">
          <LanguageToggle />
        </div>
        <OverviewCards />
      </LanguageProvider>
    </div>
  );
}
