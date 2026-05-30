/**
 * Server-side fetch helpers — Server Components uchun (SSR/ISR).
 *
 * Public catalog reads — credentials kerak emas. `next.revalidate` bilan ISR.
 * Browser axios client (client.ts) o'rniga native fetch — Next caching uchun.
 */
import type {
  Brand,
  CategoryNode,
  Paginated,
  ProductDetail,
  ProductListItem,
} from "@/types/api";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

interface FetchOpts {
  revalidate?: number;
  query?: Record<string, string | number | boolean | undefined>;
}

async function serverFetch<T>(path: string, opts: FetchOpts = {}): Promise<T> {
  const url = new URL(`${API_BASE}${path}`);
  if (opts.query) {
    for (const [k, v] of Object.entries(opts.query)) {
      if (v !== undefined && v !== "") url.searchParams.set(k, String(v));
    }
  }
  const res = await fetch(url.toString(), {
    next: { revalidate: opts.revalidate ?? 60 },
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`API ${res.status} on ${path}`);
  }
  return res.json() as Promise<T>;
}

/** Catalog server reads. Throws on error — caller may catch for fallback. */
export const serverCatalog = {
  categoryTree: () =>
    serverFetch<CategoryNode[]>("/catalog/categories/", { revalidate: 300 }),

  brands: () => serverFetch<Brand[]>("/catalog/brands/", { revalidate: 300 }),

  products: (query?: FetchOpts["query"]) =>
    serverFetch<Paginated<ProductListItem>>("/catalog/products/", {
      revalidate: 60,
      query,
    }),

  product: (slug: string) =>
    serverFetch<ProductDetail>(`/catalog/products/${slug}/`, {
      revalidate: 60,
    }),

  similar: (slug: string) =>
    serverFetch<ProductListItem[]>(`/catalog/products/${slug}/similar/`, {
      revalidate: 120,
    }),

  featured: () =>
    serverFetch<ProductListItem[]>("/catalog/products/featured/", {
      revalidate: 120,
    }),

  newArrivals: () =>
    serverFetch<ProductListItem[]>("/catalog/products/new-arrivals/", {
      revalidate: 120,
    }),

  bestsellers: () =>
    serverFetch<ProductListItem[]>("/catalog/products/bestsellers/", {
      revalidate: 120,
    }),

  search: (q: string) =>
    serverFetch<Paginated<ProductListItem>>("/catalog/search/", {
      revalidate: 30,
      query: { q },
    }),
};

/** Safe wrapper — returns fallback instead of throwing (for resilient SSR). */
export async function safe<T>(
  fn: () => Promise<T>,
  fallback: T,
): Promise<T> {
  try {
    return await fn();
  } catch {
    return fallback;
  }
}
