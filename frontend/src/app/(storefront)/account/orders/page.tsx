"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Package } from "lucide-react";
import { ordersApi } from "@/lib/api/endpoints";
import { EmptyState } from "@/components/ui/empty-state";
import { formatPrice, formatDate } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { OrderStatus } from "@/types/api";

const STATUS_LABEL: Record<OrderStatus, string> = {
  pending: "Kutilmoqda",
  confirmed: "Tasdiqlangan",
  shipped: "Jo'natilgan",
  delivered: "Yetkazilgan",
  cancelled: "Bekor qilingan",
};

const STATUS_COLOR: Record<OrderStatus, string> = {
  pending: "bg-neutral-200 text-neutral-700",
  confirmed: "bg-blue-100 text-blue-700",
  shipped: "bg-gold-400/20 text-gold-600",
  delivered: "bg-accent-700/15 text-accent-700",
  cancelled: "bg-primary-100 text-primary-700",
};

export default function OrdersPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["orders"],
    queryFn: ordersApi.list,
  });

  const orders = data?.results ?? [];

  return (
    <div>
      <h1 className="font-heading text-2xl font-bold text-neutral-900">
        Buyurtmalar
      </h1>

      {isLoading ? (
        <div className="mt-6 space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 animate-pulse rounded-xl bg-neutral-100" />
          ))}
        </div>
      ) : orders.length === 0 ? (
        <div className="mt-6">
          <EmptyState
            icon={Package}
            title="Buyurtmalar yo'q"
            description="Hali buyurtma bermadingiz."
            actionLabel="Xaridni boshlash"
            actionHref="/catalog"
          />
        </div>
      ) : (
        <div className="mt-6 space-y-3">
          {orders.map((o) => (
            <Link
              key={o.id}
              href={`/account/orders/${o.number}`}
              className="flex items-center justify-between rounded-xl border border-neutral-200 bg-white p-4 transition-colors hover:border-primary-200"
            >
              <div>
                <p className="font-medium text-neutral-900">{o.number}</p>
                <p className="text-xs text-khaki-600">
                  {formatDate(o.created_at)} · {o.items_count} mahsulot
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span
                  className={cn(
                    "rounded-full px-2.5 py-1 text-xs font-medium",
                    STATUS_COLOR[o.status],
                  )}
                >
                  {STATUS_LABEL[o.status]}
                </span>
                <span className="font-semibold text-neutral-900">
                  {formatPrice(o.total, o.currency)}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
