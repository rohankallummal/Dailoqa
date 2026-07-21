import type { ReactNode } from "react";

const columnClasses: Record<number, string> = {
  1: "grid-cols-1",
  2: "sm:grid-cols-2",
  3: "sm:grid-cols-2 lg:grid-cols-3",
  4: "sm:grid-cols-2 lg:grid-cols-4",
};

function normalize(cols: number | string | undefined): number {
  const value = typeof cols === "string" ? Number(cols) : cols;
  if (value === 1 || value === 2 || value === 3 || value === 4) return value;
  return 2;
}

export function Grid({
  cols,
  children,
}: {
  cols?: number | string;
  children: ReactNode;
}) {
  const count = normalize(cols);
  return (
    <div className={`my-5 grid grid-cols-1 gap-4 ${columnClasses[count]}`}>
      {children}
    </div>
  );
}

export function CardGroup({
  cols,
  children,
}: {
  cols?: number | string;
  children: ReactNode;
}) {
  return <Grid cols={cols}>{children}</Grid>;
}
