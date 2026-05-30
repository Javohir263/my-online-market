"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import { Heart, ShoppingBag } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ProductListItem } from "@/types/api";
import { Price } from "./price";
import { RatingStars } from "./rating-stars";
import { useAddToCart } from "@/hooks/useCart";
import { useToggleWishlist, useWishlist } from "@/hooks/useWishlist";

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
    >
      <Link
        href={`/product/${product.slug}`}
        className="group relative flex h-full flex-col overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-[var(--shadow-soft)] transition-shadow duration-300 hover:shadow-[var(--shadow-card)]"
      >
        {/* Image */}
        <div className="relative aspect-square overflow-hidden bg-neutral-100">
          {product.primary_image ? (
            <Image
              src={product.primary_image}
              alt={product.name}
              fill
              sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
              className="object-cover transition-transform duration-500 ease-out group-hover:scale-110"
            />
          ) : (
            <div className="grid h-full place-items-center bg-gradient-to-br from-neutral-100 to-neutral-200 text-2xl font-heading font-bold text-khaki-400">
              {product.name.charAt(0)}
            </div>
          )}

          {/* Badges */}
          <div className="absolute left-2.5 top-2.5 flex flex-col gap-1">
            {product.has_discount && (
              <span className="rounded-md bg-primary-500 px-2 py-0.5 text-xs font-semibold text-white shadow-sm">
                −{product.discount_percentage}%
              </span>
            )}
            {product.is_new && (
              <span className="rounded-md bg-accent-600 px-2 py-0.5 text-xs font-semibold text-white shadow-sm">
                Yangi
              </span>
            )}
          </div>

          {/* Wishlist */}
          <button
            onClick={onWishlist}
            aria-label="Sevimlilarga"
            className="absolute right-2.5 top-2.5 grid h-8 w-8 place-items-center rounded-full bg-white/90 text-neutral-600 shadow-sm backdrop-blur transition-colors hover:text-primary-600"
          >
            <Heart
              className={cn(
                "h-4 w-4 transition-all",
                inWishlist && "fill-primary-500 text-primary-500",
              )}
            />
          </button>

          {/* Out of stock overlay */}
          {!product.is_in_stock && (
            <div className="absolute inset-0 grid place-items-center bg-neutral-50/70 backdrop-blur-[1px]">
              <span className="rounded-md bg-neutral-900/80 px-3 py-1 text-xs font-medium text-white">
                Tugagan
              </span>
            </div>
          )}

          {/* Quick add (hover) */}
          {product.is_in_stock && (
            <button
              onClick={onQuickAdd}
              disabled={addToCart.isPending}
              className="absolute inset-x-2.5 bottom-2.5 flex translate-y-12 items-center justify-center gap-1.5 rounded-xl bg-primary-500 py-2 text-sm font-medium text-white opacity-0 shadow-lg transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100 hover:bg-primary-600 disabled:opacity-60"
            >
              <ShoppingBag className="h-4 w-4" />
              Savatga
            </button>
          )}
        </div>

        {/* Body */}
        <div className="flex flex-1 flex-col gap-1.5 p-3">
          {product.brand && (
            <span className="text-xs uppercase tracking-wide text-khaki-500">
              {product.brand.name}
            </span>
          )}
          <h3 className="line-clamp-2 text-sm font-medium text-neutral-900 transition-colors group-hover:text-primary-600">
            {product.name}
          </h3>

          {product.ratings_count > 0 && (
            <RatingStars
              value={product.ratings_avg}
              count={product.ratings_count}
              size={12}
            />
          )}

          <div className="mt-auto pt-1">
            <Price
              current={product.current_price}
              base={product.base_price}
              currency={product.currency}
              hasDiscount={product.has_discount}
            />
          </div>
        </div>
      </Link>
    </motion.div>
  );
}

export function ProductCardSkeleton() {
  return (
    <div className="flex flex-col overflow-hidden rounded-2xl border border-neutral-200 bg-white">
      <div className="aspect-square animate-pulse bg-neutral-100" />
      <div className="flex flex-col gap-2 p-3">
        <div className="h-3 w-1/3 animate-pulse rounded bg-neutral-100" />
        <div className="h-4 w-3/4 animate-pulse rounded bg-neutral-100" />
        <div className="h-5 w-1/2 animate-pulse rounded bg-neutral-100" />
      </div>
    </div>
  );
}
