"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { X } from "lucide-react";
import type { Brand, CategoryNode } from "@/types/api";
import { formatPrice } from "@/lib/format";

/**
 * Yuqorida ko'rinadigan faol filtr chip'lari — har birida "X" bilan
 * tezda olib tashlash. Foydalanuvchi qaysi filtrlar yoqilganini bir
 * qarashda ko'radi.
 */
export function ActiveFilters({
  categories,
  brands,
}: {
  categories: CategoryNode[];
  brands: Brand[];
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const chips: { label: string; remove: () => void }[] = [];

  const removeParam = (key: string) => () => {
    const p = new URLSearchParams(searchParams.toString());
    p.delete(key);
    p.delete("page");
    router.push(`${pathname}?${p.toString()}`);
  };

  const removeBoth = (k1: string, k2: string) => () => {
    const p = new URLSearchParams(searchParams.toString());
    p.delete(k1);
    p.delete(k2);
    p.delete("page");
    router.push(`${pathname}?${p.toString()}`);
  };

  // Kategoriya
  const cat = searchParams.get("category");
  if (cat) {
    // Recursive search in tree
    const findInTree = (
      list: CategoryNode[],
      slug: string,
    ): CategoryNode | null => {
      for (const c of list) {
        if (c.slug === slug) return c;
        const sub = findInTree(c.children, slug);
        if (sub) return sub;
      }
      return null;
    };
    const node = findInTree(categories, cat);
    chips.push({
      label: node?.name ?? cat,
      remove: removeParam("category"),
    });
  }

  // Brend
  const br = searchParams.get("brand");
  if (br) {
    const brand = brands.find((b) => b.slug === br);
    chips.push({
      label: brand?.name ?? br,
      remove: removeParam("brand"),
    });
  }

  // Narx
  const minP = searchParams.get("min_price");
  const maxP = searchParams.get("max_price");
  if (minP || maxP) {
    let label = "Narx: ";
    if (minP && maxP) label += `${formatPrice(minP)} – ${formatPrice(maxP)}`;
    else if (minP) label += `${formatPrice(minP)}+`;
    else if (maxP) label += `gacha ${formatPrice(maxP)}`;
    chips.push({
      label,
      remove: removeBoth("min_price", "max_price"),
    });
  }

  // Reyting
  const rate = searchParams.get("rating");
  if (rate) {
    chips.push({
      label: `${rate}★ va undan yuqori`,
      remove: removeParam("rating"),
    });
  }

  // Mavjudlik
  if (searchParams.get("in_stock") === "true") {
    chips.push({
      label: "Faqat mavjud",
      remove: removeParam("in_stock"),
    });
  }

  if (chips.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-xl border border-dashed border-neutral-200 bg-neutral-50/50 p-3">
      <span className="text-xs font-semibold uppercase tracking-wider text-khaki-700">
        Faol:
      </span>
      {chips.map((chip, i) => (
        <button
          key={i}
          onClick={chip.remove}
          className="inline-flex items-center gap-1.5 rounded-full bg-primary-50 px-3 py-1 text-xs font-medium text-primary-700 transition-colors hover:bg-primary-100"
        >
          {chip.label}
          <X className="h-3 w-3" />
        </button>
      ))}
    </div>
  );
}
