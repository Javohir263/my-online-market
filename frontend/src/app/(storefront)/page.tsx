import Link from "next/link";
import { ArrowRight, ShieldCheck, Truck, Sparkles } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const FEATURES = [
  {
    icon: Truck,
    title: "Tez yetkazib berish",
    text: "Butun O'zbekiston bo'ylab 1-3 kun ichida.",
  },
  {
    icon: ShieldCheck,
    title: "Xavfsiz to'lov",
    text: "Click, Payme yoki naqd — sizga qulay tarzda.",
  },
  {
    icon: Sparkles,
    title: "Premium sifat",
    text: "Faqat tekshirilgan sotuvchilar va asl mahsulotlar.",
  },
];

export default function HomePage() {
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
      <section className="grid grid-cols-1 gap-4 py-8 sm:grid-cols-3">
        {FEATURES.map((f) => (
          <div
            key={f.title}
            className="rounded-2xl border border-neutral-200 bg-white p-6 shadow-[var(--shadow-soft)]"
          >
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-accent-700/10 text-accent-700">
              <f.icon className="h-5 w-5" />
            </div>
            <h3 className="mt-4 font-heading text-lg font-semibold text-neutral-900">
              {f.title}
            </h3>
            <p className="mt-1 text-sm text-khaki-700">{f.text}</p>
          </div>
        ))}
      </section>

      {/* Placeholder — B14'da featured products keladi */}
      <section className="py-12 text-center">
        <h2 className="font-heading text-2xl font-bold text-neutral-900">
          Tez orada — tanlangan mahsulotlar
        </h2>
        <p className="mt-2 text-sm text-khaki-700">
          B14 bosqichida bu yerda featured / new / bestseller mahsulotlar
          ko&apos;rinadi.
        </p>
      </section>
    </div>
  );
}
