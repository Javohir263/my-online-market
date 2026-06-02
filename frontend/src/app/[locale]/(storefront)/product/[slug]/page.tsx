import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { serverCatalog, safe } from "@/lib/api/server";
import { Breadcrumbs } from "@/components/ui/breadcrumbs";
import { ProductGallery } from "@/components/product/product-gallery";
import { ProductPurchase } from "@/components/product/product-purchase";
import { ProductRow } from "@/components/product/product-row";
import { RatingStars } from "@/components/product/rating-stars";
import { TrustSignals } from "@/components/product/trust-signals";
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

      {/* Main grid — Gallery (sticky) + Purchase + Trust */}
      <div className="mt-6 grid grid-cols-1 gap-8 lg:grid-cols-[1.1fr_1fr]">
        {/* Gallery — sticky on desktop */}
        <div className="lg:sticky lg:top-24 lg:self-start">
          <ProductGallery images={product.images} name={product.name} />
        </div>

        {/* Right column: header → purchase → trust */}
        <div className="space-y-6">
          <div>
            {product.brand && (
              <span className="text-xs font-semibold uppercase tracking-wider text-khaki-500">
                {product.brand.name}
              </span>
            )}
            <h1 className="mt-1 font-heading text-2xl font-bold leading-tight text-neutral-900 sm:text-3xl">
              {product.name}
            </h1>

            <div className="mt-3 flex flex-wrap items-center gap-3">
              {product.ratings_count > 0 ? (
                <RatingStars
                  value={product.ratings_avg}
                  count={product.ratings_count}
                  size={14}
                  variant="compact"
                />
              ) : (
                <span className="text-xs text-khaki-600">
                  Hali sharhlar yo&apos;q
                </span>
              )}
              {product.is_bestseller && (
                <span className="rounded-md bg-gold-500/15 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-gold-700">
                  Bestseller
                </span>
              )}
              {product.is_new && (
                <span className="rounded-md bg-accent-700/10 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-accent-700">
                  Yangi
                </span>
              )}
            </div>

            {product.short_description && (
              <p className="mt-4 text-sm leading-relaxed text-khaki-800">
                {product.short_description}
              </p>
            )}
          </div>

          <ProductPurchase product={product} />

          <TrustSignals />
        </div>
      </div>

      {/* Description + attributes — pastda */}
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
            <dl className="mt-3 divide-y divide-neutral-200 overflow-hidden rounded-xl border border-neutral-200 bg-white">
              {product.attributes.map((attr) => (
                <div
                  key={attr.id}
                  className="flex justify-between px-4 py-3 text-sm even:bg-neutral-50/50"
                >
                  <dt className="text-khaki-600">{attr.name}</dt>
                  <dd className="font-medium text-neutral-900">{attr.value}</dd>
                </div>
              ))}
            </dl>
          </section>
        )}
      </div>

      {/* Similar */}
      {similar.length > 0 && (
        <ProductRow
          title="O'xshash mahsulotlar"
          subtitle="Sizga yoqishi mumkin"
          products={similar}
        />
      )}
    </div>
  );
}
