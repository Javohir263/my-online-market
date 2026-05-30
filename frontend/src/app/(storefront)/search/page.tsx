import type { Metadata } from "next";
import { serverCatalog, safe } from "@/lib/api/server";
import { ProductCard } from "@/components/product/product-card";
import { Breadcrumbs } from "@/components/ui/breadcrumbs";
import type { Paginated, ProductListItem } from "@/types/api";

export const revalidate = 30;

const EMPTY: Paginated<ProductListItem> = {
  count: 0,
  next: null,
  previous: null,
  results: [],
};

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}): Promise<Metadata> {
  const { q } = await searchParams;
  return { title: q ? `"${q}" — qidiruv` : "Qidiruv" };
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const query = q.trim();

  const data = query
    ? await safe(() => serverCatalog.search(query), EMPTY)
    : EMPTY;

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <Breadcrumbs
        items={[{ label: "Bosh sahifa", href: "/" }, { label: "Qidiruv" }]}
      />

      <h1 className="mt-4 font-heading text-2xl font-bold text-neutral-900">
        {query ? (
          <>
            <span className="text-khaki-600">Qidiruv:</span> {query}
          </>
        ) : (
          "Qidiruv"
        )}
      </h1>

      {!query ? (
        <p className="mt-6 text-sm text-khaki-700">
          Qidirish uchun yuqoridagi maydonga so&apos;z kiriting.
        </p>
      ) : data.results.length === 0 ? (
        <div className="mt-6 rounded-2xl border border-dashed border-neutral-300 py-20 text-center">
          <p className="font-heading text-xl text-neutral-800">
            Hech narsa topilmadi
          </p>
          <p className="mt-1 text-sm text-khaki-600">
            Boshqa so&apos;z bilan urinib ko&apos;ring.
          </p>
        </div>
      ) : (
        <>
          <p className="mb-4 mt-2 text-sm text-khaki-700">
            {data.count} ta natija
          </p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {data.results.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
