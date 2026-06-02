import { ShieldCheck, Truck, Sparkles } from "lucide-react";
import { serverCatalog, serverPromotions, safe } from "@/lib/api/server";
import { HeroBanner } from "@/components/home/hero-banner";
import { CategoryTiles } from "@/components/home/category-tiles";
import { PromoStrip } from "@/components/home/promo-strip";
import { BrandStrip } from "@/components/home/brand-strip";
import { ProductRow } from "@/components/product/product-row";

export const revalidate = 120;

const FEATURES = [
  {
    icon: Truck,
    title: "Tez yetkazib berish",
    text: "Butun O'zbekiston bo'ylab 1-3 kun ichida.",
  },
  {
    icon: ShieldCheck,
    title: "Xavfsiz to'lov",
    text: "Click, Payme yoki naqd to'lov.",
  },
  {
    icon: Sparkles,
    title: "Premium sifat",
    text: "Tekshirilgan sotuvchilardan original mahsulot.",
  },
];

export default async function HomePage() {
  const [banners, categories, brands, featured, newArrivals, bestsellers] =
    await Promise.all([
      safe(() => serverPromotions.banners("hero"), []),
      safe(serverCatalog.categoryTree, []),
      safe(serverCatalog.brands, []),
      safe(() => serverCatalog.featured(20), []),
      safe(() => serverCatalog.newArrivals(20), []),
      safe(() => serverCatalog.bestsellers(20), []),
    ]);

  const hasAnyProducts =
    featured.length > 0 || newArrivals.length > 0 || bestsellers.length > 0;

  return (
    <div className="mx-auto max-w-7xl px-4 pb-12">
      {/* 1. Hero — banner carousel + category rail */}
      <HeroBanner banners={banners} categories={categories} />

      {/* 2. Kategoriyalar — rangli gradient plitalar */}
      <CategoryTiles categories={categories} />

      {/* 3. Tanlangan mahsulotlar — carousel */}
      <ProductRow
        title="Tanlangan mahsulotlar"
        subtitle="Tahririyat tomonidan saralangan"
        products={featured}
        viewAllHref="/catalog?is_featured=true"
      />

      {/* 4. Promo strip — yetkazib berish + chegirma + to'lov */}
      <PromoStrip />

      {/* 5. Yangi kelganlar — carousel */}
      <ProductRow
        title="Yangi kelganlar"
        subtitle="Eng so'nggi qo'shilgan mahsulotlar"
        products={newArrivals}
        viewAllHref="/catalog?is_new=true"
      />

      {/* 6. Brendlar strip */}
      <BrandStrip brands={brands} />

      {/* 7. Eng ko'p sotilganlar — carousel */}
      <ProductRow
        title="Eng ko'p sotilganlar"
        subtitle="Mijozlarimiz orasida sevimli"
        products={bestsellers}
        viewAllHref="/catalog?is_bestseller=true"
      />

      {/* 8. Trust features — sahifa pastida */}
      <section className="mt-4 grid grid-cols-1 gap-4 py-4 sm:grid-cols-3">
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

      {/* Empty-state — agar hech qanday mahsulot bo'lmasa */}
      {!hasAnyProducts && (
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
