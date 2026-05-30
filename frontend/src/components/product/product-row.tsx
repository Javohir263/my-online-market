import Link from "next/link";
import { ArrowRight } from "lucide-react";
import type { ProductListItem } from "@/types/api";
import { ProductCard } from "./product-card";

export function ProductRow({
  title,
  products,
  viewAllHref,
}: {
  title: string;
  products: ProductListItem[];
  viewAllHref?: string;
}) {
  if (!products.length) return null;

  return (
    <section className="py-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-heading text-2xl font-bold text-neutral-900">
          {title}
        </h2>
        {viewAllHref && (
          <Link
            href={viewAllHref}
            className="flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            Barchasi
            <ArrowRight className="h-4 w-4" />
          </Link>
        )}
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {products.slice(0, 10).map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </section>
  );
}
