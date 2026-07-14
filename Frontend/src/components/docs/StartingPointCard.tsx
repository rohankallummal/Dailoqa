import Link from "next/link";
import Image from "next/image";
import { ChevronRight } from "lucide-react";
import type { StartingPoint } from "./startingPoints";

export function StartingPointCard({
  image,
  title,
  description,
  href,
  priority = false,
}: StartingPoint & { priority?: boolean }) {
  return (
    <Link
      href={href}
      className="group flex flex-col overflow-hidden rounded-2xl border border-line bg-white shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-md"
    >
      <span className="relative block aspect-[3/2] w-full border-b border-line">
        <Image
          src={image}
          alt=""
          fill
          priority={priority}
          sizes="(min-width: 1024px) 360px, (min-width: 640px) 45vw, 90vw"
          className="object-cover"
        />
      </span>
      <div className="flex flex-1 flex-col p-6">
        <h3 className="text-base font-semibold text-ink">{title}</h3>
        <p className="mt-2 flex-1 text-sm leading-relaxed text-ink-soft">
          {description}
        </p>
        <span className="mt-5 inline-flex w-fit items-center gap-1 text-sm font-medium text-ink-muted transition-colors group-hover:text-accent">
          Get started
          <ChevronRight className="h-4 w-4" />
        </span>
      </div>
    </Link>
  );
}
