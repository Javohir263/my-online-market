"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { CheckCircle2, MapPin, Plus } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Breadcrumbs } from "@/components/ui/breadcrumbs";
import { EmptyState } from "@/components/ui/empty-state";
import { accountsApi, ordersApi, type Address } from "@/lib/api/endpoints";
import { useCart } from "@/hooks/useCart";
import { useAuthStore } from "@/store/auth";
import { formatPrice } from "@/lib/format";
import { cn } from "@/lib/utils";

export default function CheckoutPage() {
  const router = useRouter();
  const qc = useQueryClient();
  const isAuth = useAuthStore((s) => s.isAuthenticated);
  const { data: cart } = useCart();
  const { data: addresses } = useQuery({
    queryKey: ["addresses"],
    queryFn: accountsApi.addresses,
    enabled: isAuth,
  });

  const [selectedAddr, setSelectedAddr] = useState<number | null>(null);
  const [note, setNote] = useState("");
  const idempotencyKey = useMemo(() => crypto.randomUUID(), []);

  const place = useMutation({
    mutationFn: () =>
      ordersApi.checkout(
        { address_id: selectedAddr!, customer_note: note },
        idempotencyKey,
      ),
    onSuccess: (order: { number: string }) => {
      qc.invalidateQueries({ queryKey: ["cart"] });
      toast.success("Buyurtma qabul qilindi!");
      router.push(`/account/orders/${order.number}`);
    },
    onError: () => toast.error("Buyurtma berishda xatolik"),
  });

  if (!isAuth) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <EmptyState
          icon={MapPin}
          title="Tizimga kiring"
          description="Buyurtma berish uchun akkauntingizga kiring."
          actionLabel="Kirish"
          actionHref="/login"
        />
      </div>
    );
  }

  const items = cart?.items ?? [];
  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <EmptyState
          icon={MapPin}
          title="Savatcha bo'sh"
          description="Avval mahsulot qo'shing."
          actionLabel="Katalogga o'tish"
          actionHref="/catalog"
        />
      </div>
    );
  }

  // Auto-select default / first address
  const effectiveAddr =
    selectedAddr ??
    addresses?.find((a) => a.is_default)?.id ??
    addresses?.[0]?.id ??
    null;

  return (
    <div className="mx-auto max-w-5xl px-4 py-6">
      <Breadcrumbs
        items={[
          { label: "Savatcha", href: "/cart" },
          { label: "Rasmiylashtirish" },
        ]}
      />
      <h1 className="mt-4 font-heading text-3xl font-bold text-neutral-900">
        Rasmiylashtirish
      </h1>

      <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-[1fr_360px]">
        {/* Left: address + note */}
        <div className="space-y-6">
          <section>
            <h2 className="mb-3 font-heading text-lg font-semibold text-neutral-900">
              Yetkazib berish manzili
            </h2>
            {!addresses || addresses.length === 0 ? (
              <Link
                href="/account/addresses"
                className="flex items-center gap-2 rounded-2xl border border-dashed border-neutral-300 p-5 text-sm text-primary-600 hover:bg-primary-50"
              >
                <Plus className="h-4 w-4" />
                Manzil qo&apos;shish
              </Link>
            ) : (
              <div className="space-y-2">
                {addresses.map((a: Address) => (
                  <button
                    key={a.id}
                    onClick={() => setSelectedAddr(a.id)}
                    className={cn(
                      "flex w-full items-start gap-3 rounded-2xl border p-4 text-left transition-colors",
                      effectiveAddr === a.id
                        ? "border-primary-500 bg-primary-50"
                        : "border-neutral-200 hover:border-neutral-300",
                    )}
                  >
                    <span
                      className={cn(
                        "mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full border-2",
                        effectiveAddr === a.id
                          ? "border-primary-500 bg-primary-500"
                          : "border-neutral-300",
                      )}
                    >
                      {effectiveAddr === a.id && (
                        <span className="h-2 w-2 rounded-full bg-white" />
                      )}
                    </span>
                    <div>
                      <p className="font-medium text-neutral-900">
                        {a.recipient_name} · {a.recipient_phone}
                      </p>
                      <p className="text-sm text-khaki-700">
                        {[a.region, a.city, a.street, a.building]
                          .filter(Boolean)
                          .join(", ")}
                      </p>
                    </div>
                  </button>
                ))}
                <Link
                  href="/account/addresses"
                  className="inline-flex items-center gap-1 text-sm text-primary-600 hover:underline"
                >
                  <Plus className="h-3.5 w-3.5" />
                  Yangi manzil
                </Link>
              </div>
            )}
          </section>

          <section>
            <h2 className="mb-3 font-heading text-lg font-semibold text-neutral-900">
              Izoh (ixtiyoriy)
            </h2>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
              placeholder="Yetkazib berish bo'yicha izoh..."
              className="w-full rounded-xl border border-neutral-200 p-3 text-sm focus:border-primary-400 focus:outline-none"
            />
          </section>
        </div>

        {/* Right: summary */}
        <aside className="h-fit space-y-4 rounded-2xl border border-neutral-200 bg-white p-5">
          <h2 className="font-heading text-lg font-semibold text-neutral-900">
            Buyurtma
          </h2>
          <div className="max-h-60 space-y-2 overflow-auto">
            {items.map((it) => (
              <div key={it.id} className="flex justify-between text-sm">
                <span className="text-khaki-700 line-clamp-1">
                  {it.product.name} × {it.quantity}
                </span>
                <span className="shrink-0 font-medium">
                  {formatPrice(it.line_total, it.product.currency)}
                </span>
              </div>
            ))}
          </div>
          <div className="space-y-1.5 border-t border-neutral-200 pt-3 text-sm">
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
            disabled={!effectiveAddr || place.isPending}
            onClick={() => {
              if (effectiveAddr) {
                setSelectedAddr(effectiveAddr);
                place.mutate();
              }
            }}
            className="h-11 w-full bg-primary-500 text-white hover:bg-primary-600"
          >
            <CheckCircle2 className="mr-1.5 h-4 w-4" />
            {place.isPending ? "Yuborilmoqda..." : "Buyurtma berish"}
          </Button>
          <p className="text-center text-xs text-khaki-500">
            To&apos;lov: yetkazib berishda (simulyatsiya)
          </p>
        </aside>
      </div>
    </div>
  );
}
