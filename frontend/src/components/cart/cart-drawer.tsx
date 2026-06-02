"use client";

import Image from "next/image";
import { Link } from "@/i18n/navigation";
import { Minus, Plus, ShoppingBag, Trash2 } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { useUIStore } from "@/store/ui";
import {
  useCart,
  useRemoveCartItem,
  useUpdateCartItem,
} from "@/hooks/useCart";
import { formatPrice } from "@/lib/format";

export function CartDrawer() {
  const open = useUIStore((s) => s.cartDrawerOpen);
  const closeCart = useUIStore((s) => s.closeCart);
  const { data: cart, isLoading } = useCart();
  const updateItem = useUpdateCartItem();
  const removeItem = useRemoveCartItem();

  const items = cart?.items ?? [];

  return (
    <Sheet open={open} onOpenChange={(o) => !o && closeCart()}>
      <SheetContent className="flex w-full flex-col gap-0 p-0 sm:max-w-md">
        <SheetHeader className="border-b border-neutral-200 px-5 py-4">
          <SheetTitle className="flex items-center gap-2 font-heading text-lg">
            <ShoppingBag className="h-5 w-5 text-primary-600" />
            Savatcha
            {cart && cart.items_count > 0 && (
              <span className="text-sm font-normal text-khaki-600">
                ({cart.items_count})
              </span>
            )}
          </SheetTitle>
        </SheetHeader>

        {isLoading ? (
          <div className="flex-1 space-y-3 p-5">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex gap-3">
                <div className="h-20 w-20 animate-pulse rounded-lg bg-neutral-100" />
                <div className="flex-1 space-y-2 py-1">
                  <div className="h-3 w-3/4 animate-pulse rounded bg-neutral-100" />
                  <div className="h-3 w-1/2 animate-pulse rounded bg-neutral-100" />
                </div>
              </div>
            ))}
          </div>
        ) : items.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-3 p-8 text-center">
            <div className="grid h-16 w-16 place-items-center rounded-full bg-neutral-100">
              <ShoppingBag className="h-7 w-7 text-khaki-400" />
            </div>
            <p className="font-heading text-lg text-neutral-800">
              Savatcha bo&apos;sh
            </p>
            <p className="text-sm text-khaki-600">
              Mahsulot qo&apos;shing va xaridni boshlang.
            </p>
            <Button
              onClick={closeCart}
              className="mt-2 bg-primary-500 text-white hover:bg-primary-600"
            >
              Xaridni boshlash
            </Button>
          </div>
        ) : (
          <>
            <div className="flex-1 divide-y divide-neutral-200 overflow-auto px-5">
              {items.map((item) => (
                <div key={item.id} className="flex gap-3 py-4">
                  <Link
                    href={`/product/${item.product.slug}`}
                    onClick={closeCart}
                    className="relative h-20 w-20 shrink-0 overflow-hidden rounded-lg bg-neutral-100"
                  >
                    {item.product.primary_image ? (
                      <Image
                        src={item.product.primary_image}
                        alt={item.product.name}
                        fill
                        sizes="80px"
                        className="object-cover"
                      />
                    ) : (
                      <div className="grid h-full place-items-center text-xs text-khaki-400">
                        —
                      </div>
                    )}
                  </Link>

                  <div className="flex flex-1 flex-col">
                    <div className="flex items-start justify-between gap-2">
                      <Link
                        href={`/product/${item.product.slug}`}
                        onClick={closeCart}
                        className="line-clamp-2 text-sm font-medium text-neutral-900 hover:text-primary-600"
                      >
                        {item.product.name}
                      </Link>
                      <button
                        onClick={() => removeItem.mutate(item.id)}
                        className="text-khaki-400 hover:text-primary-600"
                        aria-label="O'chirish"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    {item.variant && (
                      <span className="text-xs text-khaki-500">
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
                          className="grid h-7 w-7 place-items-center text-neutral-600 disabled:opacity-40"
                        >
                          <Minus className="h-3 w-3" />
                        </button>
                        <span className="w-7 text-center text-xs font-medium">
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
                          className="grid h-7 w-7 place-items-center text-neutral-600 disabled:opacity-40"
                        >
                          <Plus className="h-3 w-3" />
                        </button>
                      </div>
                      <span className="text-sm font-semibold text-neutral-900">
                        {formatPrice(item.line_total, item.product.currency)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div className="border-t border-neutral-200 bg-neutral-50 px-5 py-4">
              {cart && Number(cart.discount_amount) > 0 && (
                <div className="mb-1 flex justify-between text-sm text-accent-600">
                  <span>Chegirma</span>
                  <span>−{formatPrice(cart.discount_amount)}</span>
                </div>
              )}
              <div className="mb-3 flex justify-between">
                <span className="text-sm text-khaki-700">Jami</span>
                <span className="font-heading text-lg font-bold text-neutral-900">
                  {formatPrice(cart?.total ?? "0")}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant="outline"
                  onClick={closeCart}
                  className="border-neutral-300"
                  nativeButton={false}
                  render={<Link href="/cart" />}
                >
                  Savatcha
                </Button>
                <Button
                  className="bg-primary-500 text-white hover:bg-primary-600"
                  onClick={closeCart}
                  nativeButton={false}
                  render={<Link href="/checkout" />}
                >
                  Rasmiylashtirish
                </Button>
              </div>
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
