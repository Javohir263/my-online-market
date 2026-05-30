"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
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
    <aside className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-heading text-lg font-semibold text-neutral-900">
          Filtrlar
        </h2>
        <button
          onClick={clearAll}
          className="text-xs text-primary-600 hover:underline"
        >
          Tozalash
        </button>
      </div>

      {/* Categories */}
      <FilterGroup title="Kategoriya">
        <ul className="space-y-1">
          {categories.map((cat) => (
            <li key={cat.id}>
              <button
                onClick={() => toggleParam("category", cat.slug)}
                className={cn(
                  "block w-full rounded-md px-2 py-1.5 text-left text-sm transition-colors",
                  activeCategory === cat.slug
                    ? "bg-primary-50 font-medium text-primary-700"
                    : "text-neutral-700 hover:bg-neutral-100",
                )}
              >
                {cat.name}
                <span className="ml-1 text-xs text-khaki-500">
                  ({cat.products_count})
                </span>
              </button>
            </li>
          ))}
        </ul>
      </FilterGroup>

      {/* Brands */}
      {brands.length > 0 && (
        <FilterGroup title="Brend">
          <ul className="max-h-48 space-y-1 overflow-auto">
            {brands.map((b) => (
              <li key={b.id}>
                <label className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1 text-sm text-neutral-700 hover:bg-neutral-100">
                  <input
                    type="checkbox"
                    checked={activeBrand === b.slug}
                    onChange={() => toggleParam("brand", b.slug)}
                    className="accent-primary-500"
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
        <div className="flex items-center gap-2">
          <Input
            type="number"
            placeholder="dan"
            value={minPrice}
            onChange={(e) => setMinPrice(e.target.value)}
            className="h-9"
          />
          <span className="text-khaki-400">—</span>
          <Input
            type="number"
            placeholder="gacha"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
            className="h-9"
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
        <div className="space-y-1">
          {[4, 3, 2].map((r) => (
            <button
              key={r}
              onClick={() => toggleParam("rating", String(r))}
              className={cn(
                "block w-full rounded-md px-2 py-1.5 text-left text-sm transition-colors",
                activeRating === String(r)
                  ? "bg-primary-50 font-medium text-primary-700"
                  : "text-neutral-700 hover:bg-neutral-100",
              )}
            >
              {r}★ va undan yuqori
            </button>
          ))}
        </div>
      </FilterGroup>

      {/* In stock */}
      <label className="flex cursor-pointer items-center gap-2 text-sm text-neutral-700">
        <input
          type="checkbox"
          checked={inStock}
          onChange={() => toggleParam("in_stock", "true")}
          className="accent-primary-500"
        />
        Faqat mavjudlari
      </label>
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
    <div className="border-b border-neutral-200 pb-5">
      <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-neutral-800">
        {title}
      </h3>
      {children}
    </div>
  );
}
