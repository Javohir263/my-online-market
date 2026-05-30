import { Link } from "@/i18n/navigation";
import { ArrowRight, ShieldCheck, Truck, Sparkles } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { serverCatalog, safe } from "@/lib/api/server";
import { CategoryTiles } from "@/components/home/category-tiles";
import { ProductRow } from "@/components/product/product-row";

export const revalidate = 120;

const FEATURES = [
  { icon: Truck, title: "Tez yetkazib berish", text: "Butun O'zbekiston bo'ylab 1-3 kun." },
  { icon: ShieldCheck, title: "Xavfsiz to'lov", text: "Click, Payme yoki naqd." },
  { icon: Sparkles, title: "Premium sifat", text: "Tekshirilgan sotuvchilar." },
];

export default async function HomePage() {
  const [categories, featured, newArrivals, bestsellers] = await Promise.all([
    safe(serverCatalog.categoryTree, []),
    safe(serverCatalog.featured, []),
    safe(serverCatalog.newArrivals, []),
    safe(serverCatalog.bestsellers, []),
  ]);

  return (
    <div className="mx-auto max-w-7xl px-4">
      {/* Hero */}
      <section className="relative my-8 overflow-hidden rounded-3xl bg-gradient-to-br from-primary-700 via-primary-600 to-primary-800 px-6 py-16 text-center text-white sm:py-24">
        <div className="mx-auto max-w-2xl">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-primary-200">
            Premium marketplace
          </p>
          <h1 className="font-heading text-4xl font-bold leading-tight sm:text-5xl">
            Sifat va nafosat — bir joyda
          </h1>
          <p className="mx-auto mt-5 max-w-lg text-base text-primary-100">
            My Online Market — eng yaxshi mahsulotlarni qulay narxlarda taqdim
            etadigan zamonaviy onlayn do&apos;kon.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/catalog"
              className={cn(
                buttonVariants({ size: "lg" }),
                "h-11 bg-white px-6 text-primary-700 hover:bg-neutral-100",
              )}
            >
              Xarid qilish
              <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
            <Link
              href="/catalog"
              className={cn(
                buttonVariants({ size: "lg", variant: "outline" }),
                "h-11 border-white/40 bg-transparent px-6 text-white hover:bg-white/10 hover:text-white",
              )}
            >
              Katalogni ko&apos;rish
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="grid grid-cols-1 gap-4 py-4 sm:grid-cols-3">
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
            Admin paneldan mahsulot qo&apos;shing yoki backend ishlab
            turganini tekshiring.
          </p>
        </section>
      )}
    </div>
  );
}
