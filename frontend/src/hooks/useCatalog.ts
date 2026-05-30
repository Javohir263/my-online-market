"use client";

import { useQuery } from "@tanstack/react-query";
import { catalogApi } from "@/lib/api/endpoints";

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: catalogApi.categoryTree,
    staleTime: 5 * 60 * 1000,
  });
}

export function useBrands() {
  return useQuery({
    queryKey: ["brands"],
    queryFn: catalogApi.brands,
    staleTime: 5 * 60 * 1000,
  });
}

export function useProducts(
  params: Record<string, string | number | boolean>,
) {
  return useQuery({
    queryKey: ["products", params],
    queryFn: () => catalogApi.products(params),
    placeholderData: (prev) => prev, // smooth pagination
  });
}

export function useProduct(slug: string) {
  return useQuery({
    queryKey: ["product", slug],
    queryFn: () => catalogApi.product(slug),
    enabled: !!slug,
  });
}

export function useSearch(q: string) {
  return useQuery({
    queryKey: ["search", q],
    queryFn: () => catalogApi.search(q),
    enabled: q.trim().length >= 2,
  });
}
