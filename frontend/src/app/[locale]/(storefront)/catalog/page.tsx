import type { Metadata } from "next";
import { serverCatalog, safe } from "@/lib/api/server";
import { FilterSidebar } from "@/components/catalog/filter-sidebar";
import { ActiveFilters } from "@/components/catalog/active-filters";
import { SortDropdown } from "@/components/catalog/sort-dropdown";
import { CatalogPagination } from "@/components/catalog/catalog-pagination";
import { ProductCard } from "@/components/product/product-card";
import { Breadcrumbs } from "@/components/ui/breadcrumbs";
import { SearchX } from "lucide-react";
import type { Paginated, ProductListItem } from "@/types/api";

export const metadata: Metadata = {
  title: "Katalog",
  description: "Barcha mahsulotlar — filtrlash va saralash bilan.",
};

const PAGE_SIZE = 24;
const EMPTY: Paginated<ProductListItem> = {
  count: 0,
  next: null,
  previous: null,
  results: [],
};

type SP = Record<string, string | string[] | undefined>;

export default async function CatalogPage({
  searchParams,
}: {
  searchParams: Promise<SP>;
}) {
  const sp = await searchParams;

  // Normalize → query object for API
  const query: Record<string, string> = {};
  for (const key of [
    "category",
    "brand",
    "min_price",
    "max_price",
    "rating",
    "in_stock",
    "sort",
    "search",
    "is_featured",
    "is_new",
    "is_bestseller",
  ]) {
    const v = sp[key];
    if (typeof v === "string" && v) query[key] = v;
  }
  const page = Number(sp.page ?? 1) || 1;
  query.page = String(page);
  query.page_size = String(PAGE_SIZE);

  const [data, categories, brands] = await Promise.all([
    safe(() => serverCatalog.products(query), EMPTY),
    safe(serverCatalog.categoryTree, []),
    safe(serverCatalog.brands, []),
  ]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <Breadcrumbs
        items={[{ label: "Bosh sahifa", href: "/" }, { label: "Katalog" }]}
      />

      {/* Top header bar */}
      <div className="mt-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-heading text-3xl font-bold text-neutral-900 sm:text-4xl">
            Katalog
          </h1>
          <p className="mt-1 text-sm text-khaki-700">
            <span className="font-semibold text-neutral-800">{data.count}</span>{" "}
            ta mahsulot topildi
          </p>
        </div>
        <SortDropdown />
      </div>

      {/* Active filter chips */}
      <div className="mt-4">
        <ActiveFilters categories={categories} brands={brands} />
      </div>

      <div className="mt-5 grid grid-cols-1 gap-6 lg:grid-cols-[260px_1fr]">
        {/* Sidebar */}
        <div className="hidden lg:block">
          <FilterSidebar categories={categories} brands={brands} />
        </div>

        {/* Grid */}
        <div className="min-w-0">
          {data.results.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-neutral-300 bg-white py-24 text-center">
              <span className="grid h-16 w-16 place-items-center rounded-full bg-neutral-100 text-khaki-500">
                <SearchX className="h-7 w-7" />
              </span>
              <p className="mt-4 font-heading text-xl font-semibold text-neutral-800">
                Mahsulot topilmadi
              </p>
              <p className="mt-1.5 max-w-sm text-sm text-khaki-600">
                Tanlangan filtrlarga mos mahsulot yo&apos;q. Filtrlarni
                o&apos;zgartirib yoki tozalab ko&apos;ring.
              </p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-4">
                {data.results.map((p) => (
                  <ProductCard key={p.id} product={p} />
                ))}
              </div>
              <div className="mt-8">
                <CatalogPagination
                  page={page}
                  pageSize={PAGE_SIZE}
                  total={data.count}
                />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
