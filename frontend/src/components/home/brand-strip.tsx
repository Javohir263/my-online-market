import { Link } from "@/i18n/navigation";
import { ArrowRight } from "lucide-react";
import type { Brand } from "@/types/api";

/**
 * Brand strip — gorizontal scroll bilan brend kartochkalari.
 * Logotipi yo'q bo'lsa, brend nomi gold accent bilan ko'rsatiladi.
 */
export function BrandStrip({ brands }: { brands: Brand[] }) {
  const visible = brands.filter((b) => b.is_active).slice(0, 24);
  if (visible.length === 0) return null;

  return (
    <section className="py-8">
      <div className="mb-5 flex items-end justify-between gap-4">
        <div>
          <h2 className="font-heading text-2xl font-bold text-neutral-900 sm:text-3xl">
            Mashhur brendlar
          </h2>
          <p className="mt-1 text-sm text-khaki-700">
            Ishonchli sotuvchilardan sifatli mahsulotlar
          </p>
        </div>
        <Link
          href="/catalog"
          className="hidden items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700 sm:flex"
        >
          Barchasi
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      <div className="-mx-4 flex snap-x snap-mandatory gap-3 overflow-x-auto scroll-smooth px-4 pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {visible.map((b) => (
          <Link
            key={b.id}
            href={`/catalog?brand=${b.slug}`}
            className="group flex w-[140px] shrink-0 snap-start flex-col items-center justify-center rounded-2xl border border-neutral-200 bg-white px-3 py-5 text-center shadow-[var(--shadow-soft)] transition-all hover:-translate-y-1 hover:border-gold-400 hover:shadow-[var(--shadow-card)] sm:w-[160px]"
          >
            <span className="grid h-12 w-12 place-items-center rounded-xl bg-neutral-50 font-heading text-xl font-bold text-primary-700 transition-colors group-hover:bg-gold-400/15 group-hover:text-gold-600">
              {b.name.charAt(0).toUpperCase()}
            </span>
            <span className="mt-2.5 line-clamp-1 text-sm font-semibold text-neutral-900">
              {b.name}
            </span>
            <span className="mt-0.5 text-[10px] uppercase tracking-wider text-khaki-500">
              Brend
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
