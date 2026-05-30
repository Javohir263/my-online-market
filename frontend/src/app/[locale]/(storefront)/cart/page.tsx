"use client";

import Image from "next/image";
import { Link } from "@/i18n/navigation";
import { Minus, Plus, ShoppingBag, Tag, Trash2, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Breadcrumbs } from "@/components/ui/breadcrumbs";
import { EmptyState } from "@/components/ui/empty-state";
import {
  useApplyCoupon,
  useCart,
  useRemoveCartItem,
  useRemoveCoupon,
  useUpdateCartItem,
} from "@/hooks/useCart";
import { formatPrice } from "@/lib/format";

export default function CartPage() {
  const { data: cart, isLoading } = useCart();
  const updateItem = useUpdateCartItem();
  const removeItem = useRemoveCartItem();
  const applyCoupon = useApplyCoupon();
  const removeCoupon = useRemoveCoupon();
  const [coupon, setCoupon] = useState("");

  const items = cart?.items ?? [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <Breadcrumbs
        items={[{ label: "Bosh sahifa", href: "/" }, { label: "Savatcha" }]}
      />
      <h1 className="mt-4 font-heading text-3xl font-bold text-neutral-900">
        Savatcha
      </h1>

      {isLoading ? (
        <div className="mt-8 space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-28 animate-pulse rounded-2xl bg-neutral-100" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="mt-8">
          <EmptyState
            icon={ShoppingBag}
            title="Savatcha bo'sh"
            description="Mahsulot qo'shing va xaridni boshlang."
            actionLabel="Katalogga o'tish"
            actionHref="/catalog"
          />
        </div>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-[1fr_360px]">
          {/* Items */}
          <div className="space-y-3">
            {items.map((item) => (
              <div
                key={item.id}
                className="flex gap-4 rounded-2xl border border-neutral-200 bg-white p-4"
              >
                <Link
                  href={`/product/${item.product.slug}`}
                  className="relative h-24 w-24 shrink-0 overflow-hidden rounded-xl bg-neutral-100"
                >
                  {item.product.primary_image ? (
                    <Image
                      src={item.product.primary_image}
                      alt={item.product.name}
                      fill
                      sizes="96px"
                      className="object-cover"
                    />
                  ) : (
                    <div className="grid h-full place-items-center text-khaki-400">
                      —
                    </div>
                  )}
                </Link>

                <div className="flex flex-1 flex-col">
                  <div className="flex items-start justify-between gap-2">
                    <Link
                      href={`/product/${item.product.slug}`}
                      className="font-medium text-neutral-900 hover:text-primary-600"
                    >
                      {item.product.name}
                    </Link>
                    <button
                      onClick={() => removeItem.mutate(item.id)}
                      className="text-khaki-400 hover:text-primary-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  {item.variant && (
                    <span className="text-sm text-khaki-500">
                      {[item.variant.color, item.variant.size]
                        .filter(Boolean)
                        .join(" / ")}
                    </span>
                  )}

                  <div className="mt-auto flex items-center justify-between pt-2">
                    <div className="flex items-center rounded-lg border border-neutral-200">
                      <button
                        onClick={() =>
                          updateItem.mutate({
                            id: item.id,
                            quantity: Math.max(1, item.quantity - 1),
                          })
                        }
                        disabled={item.quantity <= 1}
                        className="grid h-8 w-8 place-items-center text-neutral-600 disabled:opacity-40"
                      >
                        <Minus className="h-3.5 w-3.5" />
                      </button>
                      <span className="w-9 text-center text-sm font-medium">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() =>
                          updateItem.mutate({
                            id: item.id,
                            quantity: item.quantity + 1,
                          })
                        }
                        disabled={item.quantity >= item.available_stock}
                        className="grid h-8 w-8 place-items-center text-neutral-600 disabled:opacity-40"
                      >
                        <Plus className="h-3.5 w-3.5" />
                      </button>
                    </div>
                    <span className="font-semibold text-neutral-900">
                      {formatPrice(item.line_total, item.product.currency)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Summary */}
          <aside className="h-fit space-y-4 rounded-2xl border border-neutral-200 bg-white p-5">
            <h2 className="font-heading text-lg font-semibold text-neutral-900">
              Buyurtma xulosasi
            </h2>

            {/* Coupon */}
            {cart?.coupon ? (
              <div className="flex items-center justify-between rounded-lg bg-accent-700/10 px-3 py-2 text-sm text-accent-700">
                <span className="flex items-center gap-1.5">
                  <Tag className="h-4 w-4" />
                  {cart.coupon.code}
                </span>
                <button onClick={() => removeCoupon.mutate()}>
                  <X className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <Input
                  placeholder="Kupon kodi"
                  value={coupon}
                  onChange={(e) => setCoupon(e.target.value)}
                  className="h-9"
                />
                <Button
                  variant="outline"
                  size="sm"
                  disabled={!coupon || applyCoupon.isPending}
                  onClick={() => applyCoupon.mutate(coupon)}
                >
                  Qo&apos;llash
                </Button>
              </div>
            )}

            <div className="space-y-2 border-t border-neutral-200 pt-3 text-sm">
              <div className="flex justify-between text-khaki-700">
                <span>Mahsulotlar</span>
                <span>{formatPrice(cart?.subtotal ?? "0")}</span>
              </div>
              {cart && Number(cart.discount_amount) > 0 && (
                <div className="flex justify-between text-accent-600">
                  <span>Chegirma</span>
                  <span>−{formatPrice(cart.discount_amount)}</span>
                </div>
              )}
              <div className="flex justify-between border-t border-neutral-200 pt-2 text-base font-bold text-neutral-900">
                <span>Jami</span>
                <span>{formatPrice(cart?.total ?? "0")}</span>
              </div>
            </div>

            <Button
              className="h-11 w-full bg-primary-500 text-white hover:bg-primary-600"
              render={<Link href="/checkout" />}
            >
              Rasmiylashtirish
            </Button>
          </aside>
        </div>
      )}
    </div>
  );
}
