"use client";

import { use } from "react";
import { Link } from "@/i18n/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowLeft } from "lucide-react";
import { ordersApi } from "@/lib/api/endpoints";
import { Button } from "@/components/ui/button";
import { formatPrice, formatDate } from "@/lib/format";

interface OrderItem {
  id: number;
  product_name_snapshot: string;
  variant_label_snapshot: string;
  quantity: number;
  price_at_purchase: string;
  line_total: string;
  product_image_snapshot: string;
}

interface OrderDetail {
  number: string;
  status: string;
  currency: string;
  subtotal: string;
  discount_amount: string;
  total: string;
  shipping_address: Record<string, string>;
  items: OrderItem[];
  created_at: string;
}

export default function OrderDetailPage({
  params,
}: {
  params: Promise<{ number: string }>;
}) {
  const { number } = use(params);
  const qc = useQueryClient();

  const { data: order, isLoading } = useQuery<OrderDetail>({
    queryKey: ["order", number],
    queryFn: () => ordersApi.detail(number) as Promise<OrderDetail>,
  });

  const cancel = useMutation({
    mutationFn: () => ordersApi.cancel(number, "Mijoz bekor qildi"),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["order", number] });
      qc.invalidateQueries({ queryKey: ["orders"] });
      toast.success("Buyurtma bekor qilindi");
    },
    onError: () => toast.error("Bekor qilib bo'lmadi"),
  });

  if (isLoading || !order) {
    return <div className="h-64 animate-pulse rounded-2xl bg-neutral-100" />;
  }

  const addr = order.shipping_address;
  const canCancel = ["pending", "confirmed"].includes(order.status);

  return (
    <div>
      <Link
        href="/account/orders"
        className="mb-4 inline-flex items-center gap-1 text-sm text-khaki-600 hover:text-primary-600"
      >
        <ArrowLeft className="h-4 w-4" />
        Buyurtmalarga qaytish
      </Link>

      <div className="flex items-center justify-between">
        <h1 className="font-heading text-2xl font-bold text-neutral-900">
          {order.number}
        </h1>
        {canCancel && (
          <Button
            variant="outline"
            size="sm"
            disabled={cancel.isPending}
            onClick={() => cancel.mutate()}
            className="border-primary-200 text-primary-600 hover:bg-primary-50"
          >
            Bekor qilish
          </Button>
        )}
      </div>
      <p className="mt-1 text-sm text-khaki-600">
        {formatDate(order.created_at)}
      </p>

      {/* Items */}
      <div className="mt-6 divide-y divide-neutral-200 rounded-2xl border border-neutral-200 bg-white">
        {order.items.map((it) => (
          <div key={it.id} className="flex items-center gap-4 p-4">
            <div className="flex-1">
              <p className="font-medium text-neutral-900">
                {it.product_name_snapshot}
              </p>
              {it.variant_label_snapshot && (
                <p className="text-xs text-khaki-500">
                  {it.variant_label_snapshot}
                </p>
              )}
              <p className="text-sm text-khaki-600">
                {it.quantity} × {formatPrice(it.price_at_purchase, order.currency)}
              </p>
            </div>
            <span className="font-semibold text-neutral-900">
              {formatPrice(it.line_total, order.currency)}
            </span>
          </div>
        ))}
      </div>

      {/* Summary + address */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border border-neutral-200 bg-white p-5">
          <h3 className="mb-3 font-semibold text-neutral-900">Yetkazib berish</h3>
          <p className="text-sm text-khaki-700">
            {addr.recipient_name}
            <br />
            {addr.recipient_phone}
            <br />
            {[addr.region, addr.city, addr.street, addr.building]
              .filter(Boolean)
              .join(", ")}
          </p>
        </div>
        <div className="rounded-2xl border border-neutral-200 bg-white p-5">
          <h3 className="mb-3 font-semibold text-neutral-900">To&apos;lov</h3>
          <div className="space-y-1.5 text-sm">
            <div className="flex justify-between text-khaki-700">
              <span>Mahsulotlar</span>
              <span>{formatPrice(order.subtotal, order.currency)}</span>
            </div>
            {Number(order.discount_amount) > 0 && (
              <div className="flex justify-between text-accent-600">
                <span>Chegirma</span>
                <span>−{formatPrice(order.discount_amount, order.currency)}</span>
              </div>
            )}
            <div className="flex justify-between border-t border-neutral-200 pt-1.5 font-bold text-neutral-900">
              <span>Jami</span>
              <span>{formatPrice(order.total, order.currency)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
