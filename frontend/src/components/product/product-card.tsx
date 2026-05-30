import Image from "next/image";
import Link from "next/link";
import { cn } from "@/lib/utils";
import type { ProductListItem } from "@/types/api";
import { Price } from "./price";
import { RatingStars } from "./rating-stars";

export function ProductCard({ product }: { product: ProductListItem }) {
  return (
    <Link
      href={`/product/${product.slug}`}
      className="group flex flex-col overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-[var(--shadow-soft)] transition-all hover:shadow-[var(--shadow-card)] hover:-translate-y-0.5"
    >
      {/* Image */}
      <div className="relative aspect-square overflow-hidden bg-neutral-100">
        {product.primary_image ? (
          <Image
            src={product.primary_image}
            alt={product.name}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="grid h-full place-items-center text-khaki-400">
            <span className="text-xs">Rasm yo&apos;q</span>
          </div>
        )}

        {/* Badges */}
        <div className="absolute left-2 top-2 flex flex-col gap-1">
          {product.has_discount && (
            <span className="rounded-md bg-primary-500 px-2 py-0.5 text-xs font-semibold text-white">
              -{product.discount_percentage}%
            </span>
          )}
          {product.is_new && (
            <span className="rounded-md bg-accent-600 px-2 py-0.5 text-xs font-semibold text-white">
              Yangi
            </span>
          )}
        </div>

        {!product.is_in_stock && (
          <div className="absolute inset-0 grid place-items-center bg-neutral-50/70">
            <span className="rounded-md bg-neutral-900/80 px-3 py-1 text-xs font-medium text-white">
              Tugagan
            </span>
          </div>
        )}
      </div>

      {/* Body */}
      <div className="flex flex-1 flex-col gap-1.5 p-3">
        {product.brand && (
          <span className="text-xs uppercase tracking-wide text-khaki-500">
            {product.brand.name}
          </span>
        )}
        <h3
          className={cn(
            "line-clamp-2 text-sm font-medium text-neutral-900",
            "group-hover:text-primary-600 transition-colors",
          )}
        >
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
