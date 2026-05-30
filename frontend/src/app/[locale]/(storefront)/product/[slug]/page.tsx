import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { serverCatalog, safe } from "@/lib/api/server";
import { Breadcrumbs } from "@/components/ui/breadcrumbs";
import { ProductGallery } from "@/components/product/product-gallery";
import { ProductPurchase } from "@/components/product/product-purchase";
import { ProductRow } from "@/components/product/product-row";
import { RatingStars } from "@/components/product/rating-stars";
import type { ProductDetail } from "@/types/api";

export const revalidate = 60;

async function getProduct(slug: string): Promise<ProductDetail | null> {
  try {
    return await serverCatalog.product(slug);
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const product = await getProduct(slug);
  if (!product) return { title: "Mahsulot topilmadi" };

  const desc =
    product.short_description ||
    product.description.slice(0, 160) ||
    product.name;

  return {
    title: product.name,
    description: desc,
    openGraph: {
      title: product.name,
      description: desc,
      images: product.primary_image ? [product.primary_image] : [],
      type: "website",
    },
  };
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const product = await getProduct(slug);
  if (!product) notFound();

  const similar = await safe(() => serverCatalog.similar(slug), []);

  // JSON-LD Product schema (Google Rich Results)
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: product.name,
    description: product.short_description || product.description,
    sku: product.sku,
    image: product.images.map((i) => i.image),
    brand: product.brand
      ? { "@type": "Brand", name: product.brand.name }
      : undefined,
    aggregateRating:
      product.ratings_count > 0
        ? {
            "@type": "AggregateRating",
            ratingValue: product.ratings_avg,
            reviewCount: product.ratings_count,
          }
        : undefined,
    offers: {
      "@type": "Offer",
      price: product.current_price,
      priceCurrency: product.currency,
      availability: product.is_in_stock
        ? "https://schema.org/InStock"
        : "https://schema.org/OutOfStock",
    },
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <Breadcrumbs
        items={[
          { label: "Bosh sahifa", href: "/" },
          { label: "Katalog", href: "/catalog" },
          {
            label: product.category.name,
            href: `/catalog?category=${product.category.slug}`,
          },
          { label: product.name },
        ]}
      />

      <div className="mt-6 grid grid-cols-1 gap-8 lg:grid-cols-2">
        <ProductGallery images={product.images} name={product.name} />

        <div>
          {product.brand && (
            <span className="text-sm uppercase tracking-wide text-khaki-500">
              {product.brand.name}
            </span>
          )}
          <h1 className="mt-1 font-heading text-3xl font-bold text-neutral-900">
            {product.name}
          </h1>

          {product.ratings_count > 0 && (
            <div className="mt-2">
              <RatingStars
                value={product.ratings_avg}
                count={product.ratings_count}
              />
            </div>
          )}

          {product.short_description && (
            <p className="mt-4 text-sm leading-relaxed text-khaki-700">
              {product.short_description}
            </p>
          )}

          <div className="mt-6 border-t border-neutral-200 pt-6">
            <ProductPurchase product={product} />
          </div>
        </div>
      </div>

      {/* Description + attributes */}
      <div className="mt-12 grid grid-cols-1 gap-8 lg:grid-cols-2">
        {product.description && (
          <section>
            <h2 className="font-heading text-xl font-bold text-neutral-900">
              Tavsif
            </h2>
            <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-khaki-800">
              {product.description}
            </p>
          </section>
        )}

        {product.attributes.length > 0 && (
          <section>
            <h2 className="font-heading text-xl font-bold text-neutral-900">
              Xususiyatlar
            </h2>
            <dl className="mt-3 divide-y divide-neutral-200 rounded-xl border border-neutral-200">
              {product.attributes.map((attr) => (
                <div
                  key={attr.id}
                  className="flex justify-between px-4 py-2.5 text-sm"
                >
                  <dt className="text-khaki-600">{attr.name}</dt>
                  <dd className="font-medium text-neutral-800">
                    {attr.value}
                  </dd>
                </div>
              ))}
            </dl>
          </section>
        )}
      </div>

      {/* Similar */}
      {similar.length > 0 && (
        <ProductRow title="O'xshash mahsulotlar" products={similar} />
      )}
    </div>
  );
}
