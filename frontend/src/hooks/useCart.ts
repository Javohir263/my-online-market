"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { toast } from "sonner";
import { cartApi } from "@/lib/api/endpoints";
import type { Cart } from "@/types/api";

const CART_KEY = ["cart"];

export function useCart() {
  return useQuery<Cart>({
    queryKey: CART_KEY,
    queryFn: cartApi.get,
    staleTime: 30 * 1000,
  });
}

export function useAddToCart() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: cartApi.addItem,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: CART_KEY });
      toast.success("Savatga qo'shildi");
    },
    onError: (err: unknown) => {
      const detail = extractError(err);
      toast.error(detail ?? "Xatolik yuz berdi");
    },
  });
}

export function useUpdateCartItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, quantity }: { id: number; quantity: number }) =>
      cartApi.updateItem(id, quantity),
    onSuccess: () => qc.invalidateQueries({ queryKey: CART_KEY }),
    onError: (err) => toast.error(extractError(err) ?? "Xatolik"),
  });
}

export function useRemoveCartItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => cartApi.removeItem(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: CART_KEY });
      toast.success("O'chirildi");
    },
  });
}

export function useApplyCoupon() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (code: string) => cartApi.applyCoupon(code),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: CART_KEY });
      toast.success("Kupon qo'llandi");
    },
    onError: (err) => toast.error(extractError(err) ?? "Kupon yaroqsiz"),
  });
}

export function useRemoveCoupon() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: cartApi.removeCoupon,
    onSuccess: () => qc.invalidateQueries({ queryKey: CART_KEY }),
  });
}

// --- helpers ---
function extractError(err: unknown): string | null {
  if (
    typeof err === "object" &&
    err !== null &&
    "response" in err &&
    typeof (err as { response?: unknown }).response === "object"
  ) {
    const data = (err as { response?: { data?: Record<string, unknown> } })
      .response?.data;
    if (data) {
      if (typeof data.detail === "string") return data.detail;
      const first = Object.values(data)[0];
      if (Array.isArray(first) && typeof first[0] === "string") return first[0];
      if (typeof first === "string") return first;
    }
  }
  return null;
}
