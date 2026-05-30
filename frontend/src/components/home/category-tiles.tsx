import Link from "next/link";
import * as Icons from "lucide-react";
import type { CategoryNode } from "@/types/api";

function getIcon(name: string): React.ComponentType<{ className?: string }> {
  // lucide-react icon name → PascalCase component
  const pascal = name
    .split("-")
    .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
    .join("");
  const Comp = (Icons as Record<string, unknown>)[pascal] as
    | React.ComponentType<{ className?: string }>
    | undefined;
  return Comp ?? Icons.Package;
}

export function CategoryTiles({ categories }: { categories: CategoryNode[] }) {
  const roots = categories.slice(0, 8);
  if (!roots.length) return null;

  return (
    <section className="py-6">
      <h2 className="mb-4 font-heading text-2xl font-bold text-neutral-900">
        Kategoriyalar
      </h2>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">
        {roots.map((cat) => {
          const Icon = getIcon(cat.icon || "package");
          return (
            <Link
              key={cat.id}
              href={`/catalog?category=${cat.slug}`}
              className="flex flex-col items-center gap-2 rounded-2xl border border-neutral-200 bg-white p-4 text-center shadow-[var(--shadow-soft)] transition-all hover:-translate-y-0.5 hover:border-primary-200 hover:shadow-[var(--shadow-card)]"
            >
              <span className="grid h-12 w-12 place-items-center rounded-full bg-primary-50 text-primary-600">
                <Icon className="h-6 w-6" />
              </span>
              <span className="line-clamp-2 text-xs font-medium text-neutral-800">
                {cat.name}
              </span>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
