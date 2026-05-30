"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api/client";
import { useAuthStore } from "@/store/auth";
import type { ProductListItem } from "@/types/api";

interface WishlistEntry {
  id: number;
  product: ProductListItem;
  created_at: string;
}

const KEY = ["wishlist"];

export function useWishlist() {
  const isAuth = useAuthStore((s) => s.isAuthenticated);
  return useQuery({
    queryKey: KEY,
    queryFn: () =>
      api
        .get<{ results: WishlistEntry[] }>("/wishlist/")
        .then((r) => r.data.results),
    enabled: isAuth,
    staleTime: 60 * 1000,
  });
}

export function useToggleWishlist() {
  const qc = useQueryClient();
  const isAuth = useAuthStore((s) => s.isAuthenticated);

  const add = useMutation({
    mutationFn: (productId: string) =>
      api.post("/wishlist/items/", { product_id: productId }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEY });
      toast.success("Sevimlilarga qo'shildi");
    },
  });

  const remove = useMutation({
    mutationFn: (productId: string) =>
      api.delete(`/wishlist/items/${productId}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEY });
      toast.success("Sevimlilardan olib tashlandi");
    },
  });

  const toggle = (productId: string, isInWishlist: boolean) => {
    if (!isAuth) {
      toast.error("Avval tizimga kiring");
      return;
    }
    if (isInWishlist) remove.mutate(productId);
    else add.mutate(productId);
  };

  return { toggle, isPending: add.isPending || remove.isPending };
}
