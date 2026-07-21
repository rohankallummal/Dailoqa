import Image from "next/image";

export function Logo({
  collapsed = false,
  className,
}: {
  collapsed?: boolean;
  className?: string;
}) {
  const source = collapsed ? "/Logo2.png" : "/Logo.png";
  const width = collapsed ? 163 : 753;

  return (
    <Image
      src={source}
      alt="Dailoqa"
      width={width}
      height={192}
      priority
      className={className ?? (collapsed ? "h-11 w-auto" : "h-7 w-auto")}
    />
  );
}
