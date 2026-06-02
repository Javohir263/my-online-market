"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { Star, X } from "lucide-react";
import type { Brand, CategoryNode } from "@/types/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export function FilterSidebar({
  categories,
  brands,
}: {
  categories: CategoryNode[];
  brands: Brand[];
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const activeCategory = searchParams.get("category") ?? "";
  const activeBrand = searchParams.get("brand") ?? "";
  const activeRating = searchParams.get("rating") ?? "";
  const inStock = searchParams.get("in_stock") === "true";

  const [minPrice, setMinPrice] = useState(searchParams.get("min_price") ?? "");
  const [maxPrice, setMaxPrice] = useState(searchParams.get("max_price") ?? "");

  const hasAnyActive =
    activeCategory ||
    activeBrand ||
    activeRating ||
    inStock ||
    searchParams.get("min_price") ||
    searchParams.get("max_price");

  function update(mutate: (p: URLSearchParams) => void) {
    const params = new URLSearchParams(searchParams.toString());
    mutate(params);
    params.delete("page");
    router.push(`${pathname}?${params.toString()}`);
  }

  function toggleParam(key: string, value: string) {
    update((p) => {
      if (p.get(key) === value) p.delete(key);
      else p.set(key, value);
    });
  }

  function applyPrice() {
    update((p) => {
      if (minPrice) p.set("min_price", minPrice);
      else p.delete("min_price");
      if (maxPrice) p.set("max_price", maxPrice);
      else p.delete("max_price");
    });
  }

  function clearAll() {
    setMinPrice("");
    setMaxPrice("");
    router.push(pathname);
  }

  return (
    <aside className="sticky top-24 max-h-[calc(100vh-7rem)] overflow-y-auto rounded-2xl border border-neutral-200 bg-white p-5 shadow-[var(--shadow-soft)] [scrollbar-width:thin]">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="font-heading text-lg font-bold text-neutral-900">
          Filtrlar
        </h2>
        {hasAnyActive && (
          <button
            onClick={clearAll}
            className="inline-flex items-center gap-1 rounded-md bg-primary-50 px-2.5 py-1 text-xs font-medium text-primary-700 transition-colors hover:bg-primary-100"
          >
            <X className="h-3 w-3" /> Tozalash
          </button>
        )}
      </div>

      <div className="space-y-5">
        {/* Categories */}
        <FilterGroup title="Kategoriya">
          <ul className="space-y-0.5">
            {categories.map((cat) => (
              <li key={cat.id}>
                <button
                  onClick={() => toggleParam("category", cat.slug)}
                  className={cn(
                    "flex w-full items-center justify-between rounded-md px-2 py-1.5 text-left text-sm transition-colors",
                    activeCategory === cat.slug
                      ? "bg-primary-50 font-semibold text-primary-700"
                      : "text-neutral-700 hover:bg-neutral-100",
                  )}
                >
                  <span className="truncate">{cat.name}</span>
                  <span
                    className={cn(
                      "ml-2 shrink-0 text-xs",
                      activeCategory === cat.slug
                        ? "text-primary-600"
                        : "text-khaki-500",
                    )}
                  >
                    {cat.products_count}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </FilterGroup>

        {/* Brands */}
        {brands.length > 0 && (
          <FilterGroup title="Brend">
            <ul className="max-h-56 space-y-0.5 overflow-auto pr-1 [scrollbar-width:thin]">
              {brands.map((b) => (
                <li key={b.id}>
                  <label
                    className={cn(
                      "flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors",
                      activeBrand === b.slug
                        ? "bg-primary-50 font-medium text-primary-700"
                        : "text-neutral-700 hover:bg-neutral-100",
                    )}
                  >
                    <input
                      type="checkbox"
                      checked={activeBrand === b.slug}
                      onChange={() => toggleParam("brand", b.slug)}
                      className="h-4 w-4 accent-primary-500"
                    />
                    {b.name}
                  </label>
                </li>
              ))}
            </ul>
          </FilterGroup>
        )}

        {/* Price */}
        <FilterGroup title="Narx (UZS)">
          <div className="flex items-center gap-1.5">
            <Input
              type="number"
              placeholder="dan"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              className="h-9 text-sm"
            />
            <span className="text-khaki-400">—</span>
            <Input
              type="number"
              placeholder="gacha"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              className="h-9 text-sm"
            />
          </div>
          <Button
            onClick={applyPrice}
            variant="outline"
            size="sm"
            className="mt-2 w-full"
          >
            Qo&apos;llash
          </Button>
        </FilterGroup>

        {/* Rating */}
        <FilterGroup title="Reyting">
          <div className="space-y-0.5">
            {[4, 3, 2].map((r) => {
              const selected = activeRating === String(r);
              return (
                <button
                  key={r}
                  onClick={() => toggleParam("rating", String(r))}
                  className={cn(
                    "flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-left text-sm transition-colors",
                    selected
                      ? "bg-primary-50 font-medium text-primary-700"
                      : "text-neutral-700 hover:bg-neutral-100",
                  )}
                >
                  <span className="flex items-center">
                    {Array.from({ length: r }).map((_, i) => (
                      <Star
                        key={i}
                        className="h-3.5 w-3.5 fill-gold-500 text-gold-500"
                      />
                    ))}
                  </span>
                  <span className="text-xs text-khaki-600">va undan yuqori</span>
                </button>
              );
            })}
          </div>
        </FilterGroup>

        {/* In stock — modern switch */}
        <label className="flex cursor-pointer items-center justify-between rounded-lg bg-neutral-50 px-3 py-2.5">
          <span className="text-sm font-medium text-neutral-800">
            Faqat mavjudlari
          </span>
          <span
            className={cn(
              "relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors",
              inStock ? "bg-accent-600" : "bg-neutral-300",
            )}
          >
            <input
              type="checkbox"
              checked={inStock}
              onChange={() => toggleParam("in_stock", "true")}
              className="sr-only"
            />
            <span
              className={cn(
                "inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform",
                inStock ? "translate-x-5" : "translate-x-1",
              )}
            />
          </span>
        </label>
      </div>
    </aside>
  );
}

function FilterGroup({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h3 className="mb-2 text-xs font-bold uppercase tracking-wider text-khaki-700">
        {title}
      </h3>
      {children}
    </div>
  );
}
