"use client";

import { CheckCircle2, Heart, Minus, Plus, ShoppingBag } from "lucide-react";
import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Price } from "./price";
import { cn } from "@/lib/utils";
import { useAddToCart } from "@/hooks/useCart";
import { useToggleWishlist, useWishlist } from "@/hooks/useWishlist";
import type { ProductDetail, ProductVariant } from "@/types/api";

export function ProductPurchase({ product }: { product: ProductDetail }) {
  const activeVariants = product.variants.filter((v) => v.is_active);
  const [variant, setVariant] = useState<ProductVariant | null>(
    activeVariants[0] ?? null,
  );
  const [qty, setQty] = useState(1);
  const addToCart = useAddToCart();
  const { data: wishlist } = useWishlist();
  const { toggle: toggleWish } = useToggleWishlist();
  const inWishlist = !!wishlist?.some((w) => w.product.id === product.id);

  const stock = variant ? variant.stock_quantity : product.stock_quantity;
  const inStock = stock > 0;

  const currentPrice = useMemo(() => {
    if (variant) return variant.final_price;
    return product.current_price;
  }, [variant, product.current_price]);

  const onAdd = () => {
    if (!inStock) return;
    addToCart.mutate({
      product_id: product.id,
      variant_id: variant?.id,
      quantity: qty,
    });
  };

  const colors = [...new Set(activeVariants.map((v) => v.color).filter(Boolean))];
  const sizes = [...new Set(activeVariants.map((v) => v.size).filter(Boolean))];

  return (
    <div className="space-y-6">
      {/* Narx — eng katta, e'tiborni tortadi */}
      <div className="rounded-2xl bg-neutral-50 p-5">
        <Price
          current={currentPrice}
          base={product.base_price}
          currency={product.currency}
          hasDiscount={product.has_discount && !variant}
          showInstallment
          size="lg"
        />
      </div>

      {/* Stock badge */}
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold",
            inStock
              ? "bg-accent-700/10 text-accent-700"
              : "bg-primary-50 text-primary-700",
          )}
        >
          <CheckCircle2 className="h-3.5 w-3.5" />
          {inStock ? `Mavjud — ${stock} dona` : "Hozircha tugagan"}
        </span>
        {product.sku && (
          <span className="text-xs text-khaki-600">SKU: {product.sku}</span>
        )}
      </div>

      {/* Colors */}
      {colors.length > 0 && (
        <div>
          <p className="mb-2 text-sm font-semibold text-neutral-800">
            Rang:{" "}
            <span className="font-normal text-khaki-700">{variant?.color}</span>
          </p>
          <div className="flex flex-wrap gap-2">
            {colors.map((c) => {
              const match = activeVariants.find((v) => v.color === c);
              const selected = variant?.color === c;
              return (
                <button
                  key={c}
                  onClick={() => match && setVariant(match)}
                  className={cn(
                    "rounded-lg border px-3.5 py-2 text-sm font-medium transition-all",
                    selected
                      ? "border-primary-500 bg-primary-50 text-primary-700 ring-2 ring-primary-200"
                      : "border-neutral-200 text-neutral-700 hover:border-neutral-400",
                  )}
                >
                  {c}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Sizes */}
      {sizes.length > 0 && (
        <div>
          <p className="mb-2 text-sm font-semibold text-neutral-800">
            O&apos;lcham:{" "}
            <span className="font-normal text-khaki-700">{variant?.size}</span>
          </p>
          <div className="flex flex-wrap gap-2">
            {sizes.map((s) => {
              const match = activeVariants.find(
                (v) =>
                  v.size === s && (!variant?.color || v.color === variant.color),
              );
              const selected = variant?.size === s;
              return (
                <button
                  key={s}
                  onClick={() => match && setVariant(match)}
                  disabled={!match}
                  className={cn(
                    "min-w-12 rounded-lg border px-3 py-2 text-sm font-medium transition-all disabled:cursor-not-allowed disabled:opacity-40",
                    selected
                      ? "border-primary-500 bg-primary-50 text-primary-700 ring-2 ring-primary-200"
                      : "border-neutral-200 text-neutral-700 hover:border-neutral-400",
                  )}
                >
                  {s}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Qty + Add to cart + Wishlist */}
      <div className="flex flex-wrap items-stretch gap-3 pt-2">
        <div className="flex h-11 items-center rounded-xl border border-neutral-300 bg-white">
          <button
            onClick={() => setQty((q) => Math.max(1, q - 1))}
            className="grid h-11 w-11 place-items-center text-neutral-600 hover:text-primary-600 disabled:opacity-40"
            disabled={qty <= 1}
            aria-label="Kamaytirish"
          >
            <Minus className="h-4 w-4" />
          </button>
          <span className="w-10 text-center text-sm font-semibold">{qty}</span>
          <button
            onClick={() => setQty((q) => Math.min(stock, q + 1))}
            className="grid h-11 w-11 place-items-center text-neutral-600 hover:text-primary-600 disabled:opacity-40"
            disabled={qty >= stock}
            aria-label="Ko'paytirish"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>

        <Button
          onClick={onAdd}
          disabled={!inStock || addToCart.isPending}
          className="h-11 min-w-44 flex-1 bg-primary-500 text-base font-semibold text-white hover:bg-primary-600"
        >
          <ShoppingBag className="mr-2 h-5 w-5" />
          {addToCart.isPending ? "Qo'shilmoqda..." : "Savatga qo'shish"}
        </Button>

        <button
          type="button"
          onClick={() => toggleWish(product.id, inWishlist)}
          aria-label={inWishlist ? "Sevimlilardan o'chirish" : "Sevimlilarga"}
          className={cn(
            "grid h-11 w-11 place-items-center rounded-xl border transition-colors",
            inWishlist
              ? "border-primary-500 bg-primary-50 text-primary-600"
              : "border-neutral-300 text-neutral-600 hover:border-primary-300 hover:text-primary-600",
          )}
        >
          <Heart className={cn("h-5 w-5", inWishlist && "fill-current")} />
        </button>
      </div>
    </div>
  );
}
