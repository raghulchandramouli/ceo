import Link from "next/link";

const links = [
  { href: "/brain", label: "Brain" },
  { href: "/connectors", label: "Connectors" },
] as const;

export function SiteHeader() {
  return (
    <header className="flex items-center justify-between border-b border-stone-200 py-4">
      <Link href="/" className="text-sm font-semibold tracking-tight">
        Company Brain
      </Link>
      <nav className="flex gap-4 text-sm">
        {links.map((link) => (
          <Link key={link.href} href={link.href} className="text-stone-600 hover:text-stone-900">
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
