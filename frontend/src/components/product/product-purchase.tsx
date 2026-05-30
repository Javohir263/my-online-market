"use client";

import { Minus, Plus, ShoppingBag } from "lucide-react";
import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Price } from "./price";
import { cn } from "@/lib/utils";
import { useAddToCart } from "@/hooks/useCart";
import type { ProductDetail, ProductVariant } from "@/types/api";

export function ProductPurchase({ product }: { product: ProductDetail }) {
  const activeVariants = product.variants.filter((v) => v.is_active);
  const [variant, setVariant] = useState<ProductVariant | null>(
    activeVariants[0] ?? null,
  );
  const [qty, setQty] = useState(1);
  const addToCart = useAddToCart();

  const stock = variant ? variant.stock_quantity : product.stock_quantity;
  const inStock = stock > 0;

  const currentPrice = useMemo(() => {
    if (variant) return variant.final_price;
    return product.current_price;
  }, [variant, product.current_price]);

  const onAdd = () => {
    addToCart.mutate({
      product_id: product.id,
      variant_id: variant?.id,
      quantity: qty,
    });
  };

  // Colors & sizes derived from variants
  const colors = [...new Set(activeVariants.map((v) => v.color).filter(Boolean))];
  const sizes = [...new Set(activeVariants.map((v) => v.size).filter(Boolean))];

  return (
    <div className="space-y-5">
      <Price
        current={currentPrice}
        base={product.base_price}
        currency={product.currency}
        hasDiscount={product.has_discount && !variant}
        size="lg"
      />

      {/* Colors */}
      {colors.length > 0 && (
        <div>
          <p className="mb-2 text-sm font-medium text-neutral-800">Rang</p>
          <div className="flex flex-wrap gap-2">
            {colors.map((c) => {
              const match = activeVariants.find((v) => v.color === c);
              const selected = variant?.color === c;
              return (
                <button
                  key={c}
                  onClick={() => match && setVariant(match)}
                  className={cn(
                    "rounded-lg border px-3 py-1.5 text-sm transition-colors",
                    selected
                      ? "border-primary-500 bg-primary-50 text-primary-700"
                      : "border-neutral-200 text-neutral-700 hover:border-neutral-300",
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
          <p className="mb-2 text-sm font-medium text-neutral-800">O&apos;lcham</p>
          <div className="flex flex-wrap gap-2">
            {sizes.map((s) => {
              const match = activeVariants.find(
                (v) => v.size === s && (!variant?.color || v.color === variant.color),
              );
              const selected = variant?.size === s;
              return (
                <button
                  key={s}
                  onClick={() => match && setVariant(match)}
                  disabled={!match}
                  className={cn(
                    "min-w-11 rounded-lg border px-3 py-1.5 text-sm transition-colors disabled:opacity-40",
                    selected
                      ? "border-primary-500 bg-primary-50 text-primary-700"
                      : "border-neutral-200 text-neutral-700 hover:border-neutral-300",
                  )}
                >
                  {s}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Stock */}
      <p className={cn("text-sm", inStock ? "text-accent-600" : "text-primary-600")}>
        {inStock ? `Mavjud — ${stock} dona` : "Hozircha tugagan"}
      </p>

      {/* Qty + Add */}
      <div className="flex items-center gap-3">
        <div className="flex items-center rounded-lg border border-neutral-200">
          <button
            onClick={() => setQty((q) => Math.max(1, q - 1))}
            className="grid h-10 w-10 place-items-center text-neutral-600 hover:text-primary-600 disabled:opacity-40"
            disabled={qty <= 1}
            aria-label="Kamaytirish"
          >
            <Minus className="h-4 w-4" />
          </button>
          <span className="w-10 text-center text-sm font-medium">{qty}</span>
          <button
            onClick={() => setQty((q) => Math.min(stock, q + 1))}
            className="grid h-10 w-10 place-items-center text-neutral-600 hover:text-primary-600 disabled:opacity-40"
            disabled={qty >= stock}
            aria-label="Ko'paytirish"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>

        <Button
          onClick={onAdd}
          disabled={!inStock || addToCart.isPending}
          className="h-10 flex-1 bg-primary-500 text-white hover:bg-primary-600"
        >
          <ShoppingBag className="mr-1 h-4 w-4" />
          {addToCart.isPending ? "Qo'shilmoqda..." : "Savatga qo'shish"}
        </Button>
      </div>
    </div>
  );
}
