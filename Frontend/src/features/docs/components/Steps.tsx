import {
  Children,
  cloneElement,
  isValidElement,
  type ReactElement,
  type ReactNode,
} from "react";

type StepProps = {
  title?: string;
  index?: number;
  children?: ReactNode;
};

export function Step({ title, index, children }: StepProps) {
  return (
    <li className="relative pb-6 pl-10 last:pb-0">
      <span className="absolute left-0 top-0 flex h-7 w-7 items-center justify-center rounded-full border border-line bg-white text-xs font-semibold text-ink-soft">
        {index ?? 1}
      </span>
      {title ? (
        <h4 className="mt-1 text-sm font-semibold text-ink">{title}</h4>
      ) : null}
      {children ? (
        <div className="mt-1.5 text-sm leading-relaxed text-ink-soft [&>p:first-child]:mt-0">
          {children}
        </div>
      ) : null}
    </li>
  );
}

export function Steps({ children }: { children: ReactNode }) {
  const steps = Children.toArray(children).filter((child) =>
    isValidElement(child),
  ) as ReactElement<StepProps>[];

  if (steps.length === 0) return null;

  return (
    <ol className="my-4 ml-1 border-l border-line pl-3">
      {steps.map((step, index) =>
        cloneElement(step, { key: index, index: index + 1 }),
      )}
    </ol>
  );
}
