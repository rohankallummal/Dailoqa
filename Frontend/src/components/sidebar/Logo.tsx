import Image from "next/image";

export function Logo({ className }: { className?: string }) {
  return (
    <Image
      src="/Logo.png"
      alt="Dailoqa"
      width={752}
      height={192}
      priority
      className={className ?? "h-7 w-auto"}
    />
  );
}
