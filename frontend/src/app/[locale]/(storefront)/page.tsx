import { ShieldCheck, Truck, Sparkles } from "lucide-react";
import { serverCatalog, serverPromotions, safe } from "@/lib/api/server";
import { HeroBanner } from "@/components/home/hero-banner";
import { CategoryTiles } from "@/components/home/category-tiles";
import { ProductRow } from "@/components/product/product-row";

export const revalidate = 120;

const FEATURES = [
  { icon: Truck, title: "Tez yetkazib berish", text: "Butun O'zbekiston bo'ylab 1-3 kun." },
  { icon: ShieldCheck, title: "Xavfsiz to'lov", text: "Click, Payme yoki naqd." },
  { icon: Sparkles, title: "Premium sifat", text: "Tekshirilgan sotuvchilar." },
];

export default async function HomePage() {
  const [banners, categories, featured, newArrivals, bestsellers] =
    await Promise.all([
      safe(() => serverPromotions.banners("hero"), []),
      safe(serverCatalog.categoryTree, []),
      safe(serverCatalog.featured, []),
      safe(serverCatalog.newArrivals, []),
      safe(serverCatalog.bestsellers, []),
    ]);

  return (
    <div className="mx-auto max-w-7xl px-4 pb-12">
      {/* Hero — banner carousel + category rail */}
      <HeroBanner banners={banners} categories={categories} />

      {/* Trust features */}
      <section className="grid grid-cols-1 gap-4 py-7 sm:grid-cols-3">
        {FEATURES.map((f) => (
          <div
            key={f.title}
            className="flex items-start gap-3 rounded-2xl border border-neutral-200 bg-white p-5 shadow-[var(--shadow-soft)]"
          >
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-accent-700/10 text-accent-700">
              <f.icon className="h-5 w-5" />
            </span>
            <div>
              <h3 className="font-heading font-semibold text-neutral-900">
                {f.title}
              </h3>
              <p className="text-sm text-khaki-700">{f.text}</p>
            </div>
          </div>
        ))}
      </section>

      {/* Categories */}
      <CategoryTiles categories={categories} />

      {/* Product rows */}
      <ProductRow
        title="Tanlangan mahsulotlar"
        products={featured}
        viewAllHref="/catalog?is_featured=true"
      />
      <ProductRow
        title="Yangi kelganlar"
        products={newArrivals}
        viewAllHref="/catalog?is_new=true"
      />
      <ProductRow
        title="Eng ko'p sotilganlar"
        products={bestsellers}
        viewAllHref="/catalog?is_bestseller=true"
      />

      {/* Empty-state hint */}
      {!featured.length && !newArrivals.length && !bestsellers.length && (
        <section className="py-16 text-center">
          <h2 className="font-heading text-2xl font-bold text-neutral-900">
            Hozircha mahsulotlar yo&apos;q
          </h2>
          <p className="mt-2 text-sm text-khaki-700">
            Admin paneldan mahsulot qo&apos;shing yoki backend ishlab turganini
            tekshiring.
          </p>
        </section>
      )}
    </div>
  );
}
