import Link from "next/link";
import { ChevronRight } from "lucide-react";

export interface Crumb {
  label: string;
  href?: string;
}

export function Breadcrumbs({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Breadcrumb" className="flex items-center text-sm">
      <ol className="flex flex-wrap items-center gap-1 text-khaki-600">
        {items.map((item, i) => {
          const last = i === items.length - 1;
          return (
            <li key={i} className="flex items-center gap-1">
              {item.href && !last ? (
                <Link
                  href={item.href}
                  className="transition-colors hover:text-primary-600"
                >
                  {item.label}
                </Link>
              ) : (
                <span className="font-medium text-neutral-800">
                  {item.label}
                </span>
              )}
              {!last && (
                <ChevronRight className="h-3.5 w-3.5 text-neutral-300" />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
