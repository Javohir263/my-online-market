"use client";

import { useCallback, useRef, useState } from "react";
import { Link } from "@/i18n/navigation";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import type { ProductListItem } from "@/types/api";
import { ProductCard } from "./product-card";

/**
 * Gorizontal scroll carousel (Uzum uslubida).
 * - Mobile: native swipe (touch)
 * - Desktop: prev/next tugmalari + snap scroll
 */
export function ProductRow({
  title,
  subtitle,
  products,
  viewAllHref,
}: {
  title: string;
  subtitle?: string;
  products: ProductListItem[];
  viewAllHref?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [canPrev, setCanPrev] = useState(false);
  const [canNext, setCanNext] = useState(true);

  const onScroll = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    setCanPrev(el.scrollLeft > 4);
    setCanNext(el.scrollLeft + el.clientWidth < el.scrollWidth - 4);
  }, []);

  const scrollBy = (dir: 1 | -1) => {
    const el = ref.current;
    if (!el) return;
    // Bir karta kengligi taxminan: clientWidth / visibleCount
    const step = Math.max(280, el.clientWidth * 0.7) * dir;
    el.scrollBy({ left: step, behavior: "smooth" });
  };

  if (!products.length) return null;

  return (
    <section className="py-7">
      <div className="mb-5 flex items-end justify-between gap-4">
        <div>
          <h2 className="font-heading text-2xl font-bold text-neutral-900 sm:text-3xl">
            {title}
          </h2>
          {subtitle && (
            <p className="mt-1 text-sm text-khaki-700">{subtitle}</p>
          )}
        </div>

        <div className="flex items-center gap-2">
          {viewAllHref && (
            <Link
              href={viewAllHref}
              className="hidden items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700 sm:flex"
            >
              Barchasi
              <ArrowRight className="h-4 w-4" />
            </Link>
          )}
          {/* Desktop arrows */}
          <div className="hidden items-center gap-1.5 md:flex">
            <button
              type="button"
              aria-label="Oldingi"
              onClick={() => scrollBy(-1)}
              disabled={!canPrev}
              className="grid h-9 w-9 place-items-center rounded-full border border-neutral-200 bg-white text-neutral-700 transition-colors hover:border-primary-300 hover:text-primary-600 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              type="button"
              aria-label="Keyingi"
              onClick={() => scrollBy(1)}
              disabled={!canNext}
              className="grid h-9 w-9 place-items-center rounded-full border border-neutral-200 bg-white text-neutral-700 transition-colors hover:border-primary-300 hover:text-primary-600 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Scroller */}
      <div
        ref={ref}
        onScroll={onScroll}
        className="-mx-4 flex snap-x snap-mandatory gap-3 overflow-x-auto scroll-smooth px-4 pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
      >
        {products.map((p) => (
          <div
            key={p.id}
            className="w-[160px] shrink-0 snap-start sm:w-[200px] lg:w-[220px] xl:w-[240px]"
          >
            <ProductCard product={p} />
          </div>
        ))}
      </div>

      {/* Mobile "Barchasi" link */}
      {viewAllHref && (
        <Link
          href={viewAllHref}
          className="mt-3 flex items-center justify-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700 sm:hidden"
        >
          Barchasini ko&apos;rish
          <ArrowRight className="h-4 w-4" />
        </Link>
      )}
    </section>
  );
}
