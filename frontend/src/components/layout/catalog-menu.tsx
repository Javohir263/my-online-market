"use client";

import { useEffect, useRef, useState } from "react";
import { Link } from "@/i18n/navigation";
import { ChevronRight, LayoutGrid, X } from "lucide-react";
import { useCategories } from "@/hooks/useCatalog";
import { categoryIcon } from "@/lib/category-icon";

export function CatalogMenu() {
  const { data: categories } = useCategories();
  const roots = categories ?? [];
  const [open, setOpen] = useState(false);
  const [activeId, setActiveId] = useState<number | null>(null);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const active = roots.find((r) => r.id === activeId) ?? roots[0];
  const close = () => setOpen(false);

  return (
    <div ref={ref} className="relative hidden md:block">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex h-11 items-center gap-2 rounded-xl bg-primary-500 px-4 text-sm font-semibold text-white transition-colors hover:bg-primary-600"
      >
        {open ? <X className="h-4 w-4" /> : <LayoutGrid className="h-4 w-4" />}
        Katalog
      </button>

      {open && roots.length > 0 && (
        <div className="absolute left-0 top-[calc(100%+0.5rem)] z-50 flex w-[700px] max-w-[92vw] overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-[var(--shadow-card)]">
          <ul className="max-h-[70vh] w-56 shrink-0 overflow-auto border-r border-neutral-100 bg-neutral-50 p-2">
            {roots.map((cat) => {
              const Icon = categoryIcon(cat.icon);
              const isActive = active?.id === cat.id;
              return (
                <li key={cat.id}>
                  <Link
                    href={`/catalog?category=${cat.slug}`}
                    onClick={close}
                    onMouseEnter={() => setActiveId(cat.id)}
                    className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors ${
                      isActive
                        ? "bg-white text-primary-700 shadow-sm"
                        : "text-neutral-700 hover:text-primary-700"
                    }`}
                  >
                    <Icon className="h-4 w-4 shrink-0 text-khaki-500" />
                    <span className="line-clamp-1">{cat.name}</span>
                    <ChevronRight className="ml-auto h-3.5 w-3.5 shrink-0 text-neutral-300" />
                  </Link>
                </li>
              );
            })}
          </ul>
          <div className="flex-1 p-5">
            {active && (
              <>
                <Link
                  href={`/catalog?category=${active.slug}`}
                  onClick={close}
                  className="mb-3 inline-flex items-center gap-1 font-heading text-lg font-bold text-neutral-900 hover:text-primary-700"
                >
                  {active.name}
                  <ChevronRight className="h-4 w-4" />
                </Link>
                {active.children && active.children.length > 0 ? (
                  <div className="grid grid-cols-2 gap-x-6 gap-y-0.5">
                    {active.children.map((child) => (
                      <Link
                        key={child.id}
                        href={`/catalog?category=${child.slug}`}
                        onClick={close}
                        className="truncate rounded-md py-1.5 text-sm text-neutral-600 hover:text-primary-600"
                      >
                        {child.name}
                      </Link>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-khaki-600">
                    Barcha mahsulotlarni ko&apos;rish uchun bo&apos;lim nomini
                    bosing.
                  </p>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
