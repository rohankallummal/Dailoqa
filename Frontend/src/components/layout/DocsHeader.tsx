import Image from "next/image";

export function DocsHeader() {
  return (
    <header className="flex h-16 flex-shrink-0 items-center bg-white px-6">
      <Image
        src="/DocsLogo.png"
        alt="dailoqa docs"
        width={1246}
        height={174}
        priority
        className="h-7 w-auto"
      />
    </header>
  );
}
