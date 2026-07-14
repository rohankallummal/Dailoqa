import { LanguageTabs } from "@/components/docs/LanguageTabs";
import { StartingPointCard } from "@/components/docs/StartingPointCard";
import { startingPoints } from "@/components/docs/startingPoints";

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

      <div className="mt-6">
        <LanguageTabs />
      </div>

      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {startingPoints.map((point, index) => (
          <StartingPointCard key={point.href} {...point} priority={index === 0} />
        ))}
      </div>
    </div>
  );
}
