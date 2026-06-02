"use client";

import Image from "next/image";
import { Link } from "@/i18n/navigation";
import {
  ArrowRight,
  CheckCircle2,
  Minus,
  Plus,
  ShieldCheck,
  ShoppingBag,
  Tag,
  Trash2,
  Truck,
  X,
} from "lucide-react";
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

      <div className="mt-4 flex items-end gap-3">
        <h1 className="font-heading text-3xl font-bold text-neutral-900 sm:text-4xl">
          Savatcha
        </h1>
        {cart && cart.items_count > 0 && (
          <span className="mb-1.5 text-sm font-medium text-khaki-700">
            {cart.items_count} ta mahsulot
          </span>
        )}
      </div>

      {isLoading ? (
        <div className="mt-8 space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-28 animate-pulse rounded-2xl bg-neutral-100"
            />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="mt-8">
          <EmptyState
            icon={ShoppingBag}
            title="Savatcha bo'sh"
            description="Mahsulot qo'shing va xaridni boshlang. Yuzlab tanlangan mahsulotlar sizni kutmoqda."
            actionLabel="Katalogga o'tish"
            actionHref="/catalog"
          />
        </div>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_380px]">
          {/* ─── Items ─── */}
          <div className="space-y-3">
            {items.map((item) => (
              <div
                key={item.id}
                className="flex gap-4 rounded-2xl border border-neutral-200 bg-white p-4 transition-shadow hover:shadow-[var(--shadow-soft)]"
              >
                <Link
                  href={`/product/${item.product.slug}`}
                  className="relative h-24 w-24 shrink-0 overflow-hidden rounded-xl bg-neutral-100 sm:h-28 sm:w-28"
                >
                  {item.product.primary_image ? (
                    <Image
                      src={item.product.primary_image}
                      alt={item.product.name}
                      fill
                      sizes="112px"
                      className="object-cover"
                    />
                  ) : (
                    <div className="grid h-full place-items-center text-khaki-400">
                      —
                    </div>
                  )}
                </Link>

                <div className="flex min-w-0 flex-1 flex-col">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      {item.product.brand && (
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-khaki-500">
                          {item.product.brand.name}
                        </span>
                      )}
                      <Link
                        href={`/product/${item.product.slug}`}
                        className="block truncate font-medium text-neutral-900 hover:text-primary-600"
                      >
                        {item.product.name}
                      </Link>
                      {item.variant && (
                        <span className="text-xs text-khaki-600">
                          {[item.variant.color, item.variant.size]
                            .filter(Boolean)
                            .join(" / ")}
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => removeItem.mutate(item.id)}
                      aria-label="O'chirish"
                      className="text-khaki-400 transition-colors hover:text-primary-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  <div className="mt-auto flex items-center justify-between gap-2 pt-3">
                    <div className="flex h-9 items-center rounded-lg border border-neutral-200 bg-white">
                      <button
                        onClick={() =>
                          updateItem.mutate({
                            id: item.id,
                            quantity: Math.max(1, item.quantity - 1),
                          })
                        }
                        disabled={item.quantity <= 1}
                        className="grid h-9 w-9 place-items-center text-neutral-600 hover:text-primary-600 disabled:opacity-40"
                        aria-label="Kamaytirish"
                      >
                        <Minus className="h-3.5 w-3.5" />
                      </button>
                      <span className="w-9 text-center text-sm font-semibold">
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
                        className="grid h-9 w-9 place-items-center text-neutral-600 hover:text-primary-600 disabled:opacity-40"
                        aria-label="Ko'paytirish"
                      >
                        <Plus className="h-3.5 w-3.5" />
                      </button>
                    </div>
                    <span className="font-heading text-lg font-bold text-neutral-900">
                      {formatPrice(item.line_total, item.product.currency)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* ─── Sticky Summary ─── */}
          <aside className="space-y-3 lg:sticky lg:top-24 lg:self-start">
            <div className="space-y-4 rounded-2xl border border-neutral-200 bg-white p-5 shadow-[var(--shadow-soft)]">
              <h2 className="font-heading text-lg font-bold text-neutral-900">
                Buyurtma xulosasi
              </h2>

              {/* Coupon */}
              {cart?.coupon ? (
                <div className="flex items-center justify-between rounded-xl bg-accent-700/10 px-3 py-2.5 text-sm text-accent-700">
                  <span className="flex items-center gap-2 font-semibold">
                    <Tag className="h-4 w-4" />
                    {cart.coupon.code}
                  </span>
                  <button
                    onClick={() => removeCoupon.mutate()}
                    aria-label="Kuponni olib tashlash"
                    className="rounded p-0.5 hover:bg-accent-700/15"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <div className="flex gap-2">
                  <Input
                    placeholder="Kupon kodi"
                    value={coupon}
                    onChange={(e) => setCoupon(e.target.value.toUpperCase())}
                    className="h-10"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!coupon || applyCoupon.isPending}
                    onClick={() => applyCoupon.mutate(coupon)}
                    className="h-10 shrink-0"
                  >
                    Qo&apos;llash
                  </Button>
                </div>
              )}

              <div className="space-y-2 border-t border-neutral-200 pt-4 text-sm">
                <div className="flex justify-between text-khaki-700">
                  <span>Mahsulotlar ({cart?.items_count ?? 0})</span>
                  <span className="font-medium text-neutral-800">
                    {formatPrice(cart?.subtotal ?? "0")}
                  </span>
                </div>
                {cart && Number(cart.discount_amount) > 0 && (
                  <div className="flex justify-between text-accent-700">
                    <span>Chegirma</span>
                    <span className="font-medium">
                      −{formatPrice(cart.discount_amount)}
                    </span>
                  </div>
                )}
                <div className="flex justify-between text-khaki-700">
                  <span>Yetkazib berish</span>
                  <span className="font-medium text-accent-700">Bepul</span>
                </div>
                <div className="flex items-baseline justify-between border-t border-neutral-200 pt-3">
                  <span className="text-sm font-semibold text-neutral-700">
                    Jami
                  </span>
                  <span className="font-heading text-2xl font-bold text-neutral-900">
                    {formatPrice(cart?.total ?? "0")}
                  </span>
                </div>
              </div>

              <Button
                className="h-12 w-full bg-primary-500 text-base font-semibold text-white shadow-sm hover:bg-primary-600"
                nativeButton={false}
                render={<Link href="/checkout" />}
              >
                Rasmiylashtirish
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </div>

            {/* Trust mini */}
            <ul className="space-y-2 rounded-2xl border border-neutral-200 bg-neutral-50/50 p-4 text-xs text-khaki-700">
              <li className="flex items-center gap-2">
                <Truck className="h-4 w-4 text-accent-700" />
                Bepul yetkazib berish 200,000+ buyurtmaga
              </li>
              <li className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-accent-700" />
                Click va Payme orqali xavfsiz to&apos;lov
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-accent-700" />
                14 kun ichida qaytarish imkoniyati
              </li>
            </ul>
          </aside>
        </div>
      )}
    </div>
  );
}
