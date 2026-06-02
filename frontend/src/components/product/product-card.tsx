"use client";

import Image from "next/image";
import { Link } from "@/i18n/navigation";
import { motion } from "framer-motion";
import { Heart, Plus, ShoppingBag } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ProductListItem } from "@/types/api";
import { Price } from "./price";
import { RatingStars } from "./rating-stars";
import { useAddToCart } from "@/hooks/useCart";
import { useToggleWishlist, useWishlist } from "@/hooks/useWishlist";

/**
 * Commerce-style product card (Uzum uslubida):
 *   - Rasm: aspect-square, hover'da kichik zoom
 *   - Badge'lar: chap-yuqorida discount %, "Yangi", "Top"
 *   - Wishlist: o'ng-yuqorida (kichik dumaloq tugma)
 *   - Body: brand → nom → reyting (compact) → narx (katta) → bo'lib to'lash
 *   - Quick add: kompakt "+" tugma narx yonida (har doim ko'rinadi)
 */
export function ProductCard({
  product,
  index = 0,
}: {
  product: ProductListItem;
  index?: number;
}) {
  const addToCart = useAddToCart();
  const { data: wishlist } = useWishlist();
  const { toggle } = useToggleWishlist();
  const inWishlist = !!wishlist?.some((w) => w.product.id === product.id);

  const onQuickAdd = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!product.is_in_stock) return;
    addToCart.mutate({ product_id: product.id, quantity: 1 });
  };

  const onWishlist = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    toggle(product.id, inWishlist);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.35, delay: Math.min(index * 0.04, 0.3) }}
      className="h-full"
    >
      <Link
        href={`/product/${product.slug}`}
        className="group relative flex h-full flex-col overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-[var(--shadow-soft)] transition-all duration-300 hover:-translate-y-0.5 hover:border-primary-200 hover:shadow-[var(--shadow-card)]"
      >
        {/* ─── Image ─── */}
        <div className="relative aspect-square overflow-hidden bg-neutral-100">
          {product.primary_image ? (
            <Image
              src={product.primary_image}
              alt={product.name}
              fill
              sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 240px"
              className="object-cover transition-transform duration-500 ease-out group-hover:scale-105"
            />
          ) : (
            <div className="grid h-full place-items-center bg-gradient-to-br from-neutral-100 to-neutral-200 font-heading text-3xl font-bold text-khaki-400">
              {product.name.charAt(0)}
            </div>
          )}

          {/* Badges — chap yuqorida */}
          <div className="absolute left-2.5 top-2.5 flex flex-col items-start gap-1">
            {product.has_discount && (
              <span className="rounded-md bg-primary-500 px-2 py-1 text-[11px] font-bold text-white shadow-sm">
                −{product.discount_percentage}%
              </span>
            )}
            {product.is_new && !product.has_discount && (
              <span className="rounded-md bg-accent-600 px-2 py-0.5 text-[11px] font-semibold text-white shadow-sm">
                Yangi
              </span>
            )}
            {product.is_bestseller && (
              <span className="rounded-md bg-gold-500 px-2 py-0.5 text-[11px] font-semibold text-neutral-900 shadow-sm">
                TOP
              </span>
            )}
          </div>

          {/* Wishlist — o'ng yuqorida */}
          <button
            type="button"
            onClick={onWishlist}
            aria-label={inWishlist ? "Sevimlilardan o'chirish" : "Sevimlilarga qo'shish"}
            className="absolute right-2.5 top-2.5 grid h-8 w-8 place-items-center rounded-full bg-white/95 text-neutral-700 shadow-sm backdrop-blur transition-all hover:scale-110 hover:text-primary-600"
          >
            <Heart
              className={cn(
                "h-4 w-4 transition-all",
                inWishlist && "fill-primary-500 text-primary-500",
              )}
            />
          </button>

          {/* Out-of-stock overlay */}
          {!product.is_in_stock && (
            <div className="absolute inset-0 grid place-items-center bg-neutral-50/75 backdrop-blur-[1px]">
              <span className="rounded-md bg-neutral-900/85 px-3 py-1 text-xs font-semibold text-white">
                Tugagan
              </span>
            </div>
          )}
        </div>

        {/* ─── Body ─── */}
        <div className="flex flex-1 flex-col gap-1.5 p-3">
          {product.brand && (
            <span className="text-[10px] font-semibold uppercase tracking-wider text-khaki-500">
              {product.brand.name}
            </span>
          )}

          <h3 className="line-clamp-2 min-h-[2.5rem] text-sm font-medium leading-snug text-neutral-900 transition-colors group-hover:text-primary-700">
            {product.name}
          </h3>

          {product.ratings_count > 0 && (
            <RatingStars
              value={product.ratings_avg}
              count={product.ratings_count}
              size={12}
              variant="compact"
            />
          )}

          {/* Narx + quick add — pastda */}
          <div className="mt-auto flex items-end justify-between gap-2 pt-2">
            <Price
              current={product.current_price}
              base={product.base_price}
              currency={product.currency}
              hasDiscount={product.has_discount}
              showInstallment
              size="md"
              className="min-w-0 flex-1"
            />
            {product.is_in_stock && (
              <button
                type="button"
                onClick={onQuickAdd}
                disabled={addToCart.isPending}
                aria-label="Savatga qo'shish"
                className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-primary-500 text-white shadow-sm transition-all hover:bg-primary-600 hover:scale-105 active:scale-95 disabled:opacity-60"
              >
                {addToCart.isPending ? (
                  <ShoppingBag className="h-4 w-4 animate-pulse" />
                ) : (
                  <Plus className="h-5 w-5" strokeWidth={2.5} />
                )}
              </button>
            )}
          </div>
        </div>
      </Link>
    </motion.div>
  );
}

export function ProductCardSkeleton() {
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-2xl border border-neutral-200 bg-white">
      <div className="aspect-square animate-pulse bg-neutral-100" />
      <div className="flex flex-1 flex-col gap-2 p-3">
        <div className="h-2.5 w-1/3 animate-pulse rounded bg-neutral-100" />
        <div className="h-4 w-3/4 animate-pulse rounded bg-neutral-100" />
        <div className="h-3 w-1/2 animate-pulse rounded bg-neutral-100" />
        <div className="mt-auto flex items-end justify-between gap-2 pt-2">
          <div className="h-6 w-2/3 animate-pulse rounded bg-neutral-100" />
          <div className="h-9 w-9 animate-pulse rounded-xl bg-neutral-100" />
        </div>
      </div>
    </div>
  );
}
