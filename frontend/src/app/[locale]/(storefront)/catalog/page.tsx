import type { Metadata } from "next";
import { serverCatalog, safe } from "@/lib/api/server";
import { FilterSidebar } from "@/components/catalog/filter-sidebar";
import { SortDropdown } from "@/components/catalog/sort-dropdown";
import { CatalogPagination } from "@/components/catalog/catalog-pagination";
import { ProductCard } from "@/components/product/product-card";
import { Breadcrumbs } from "@/components/ui/breadcrumbs";
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

      <div className="mt-4 flex items-center justify-between">
        <h1 className="font-heading text-3xl font-bold text-neutral-900">
          Katalog
        </h1>
        <SortDropdown />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-8 lg:grid-cols-[260px_1fr]">
        {/* Sidebar */}
        <div className="hidden lg:block">
          <FilterSidebar categories={categories} brands={brands} />
        </div>

        {/* Grid */}
        <div>
          <p className="mb-4 text-sm text-khaki-700">
            {data.count} ta mahsulot topildi
          </p>

          {data.results.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-neutral-300 py-20 text-center">
              <p className="font-heading text-xl text-neutral-800">
                Mahsulot topilmadi
              </p>
              <p className="mt-1 text-sm text-khaki-600">
                Filtrlarni o&apos;zgartiring yoki tozalang.
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
