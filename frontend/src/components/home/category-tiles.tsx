import { Link } from "@/i18n/navigation";
import { categoryIcon } from "@/lib/category-icon";
import type { CategoryNode } from "@/types/api";

/**
 * Bosh sahifa kategoriya plitalari — rangli gradient bilan.
 * Har kategoriya o'z slug'iga mos rangda bo'ladi (deterministik).
 */
const TILE_THEMES: Record<string, { gradient: string; icon: string; ring: string }> = {
  elektronika: {
    gradient: "from-indigo-500 to-blue-600",
    icon: "text-white",
    ring: "ring-indigo-300/40",
  },
  "kiyim-kechak": {
    gradient: "from-primary-500 to-primary-700",
    icon: "text-white",
    ring: "ring-primary-300/40",
  },
  "oziq-ovqat": {
    gradient: "from-amber-500 to-orange-600",
    icon: "text-white",
    ring: "ring-amber-300/40",
  },
  gozallik: {
    gradient: "from-pink-500 to-rose-600",
    icon: "text-white",
    ring: "ring-pink-300/40",
  },
  "uy-va-bog": {
    gradient: "from-accent-500 to-accent-700",
    icon: "text-white",
    ring: "ring-accent-400/40",
  },
  bolalar: {
    gradient: "from-sky-500 to-cyan-600",
    icon: "text-white",
    ring: "ring-sky-300/40",
  },
  sport: {
    gradient: "from-emerald-500 to-green-700",
    icon: "text-white",
    ring: "ring-emerald-300/40",
  },
  kitoblar: {
    gradient: "from-gold-500 to-khaki-700",
    icon: "text-white",
    ring: "ring-gold-400/40",
  },
  avtotovarlar: {
    gradient: "from-neutral-600 to-neutral-900",
    icon: "text-white",
    ring: "ring-neutral-400/40",
  },
  "hayvonlar-uchun": {
    gradient: "from-teal-500 to-emerald-700",
    icon: "text-white",
    ring: "ring-teal-300/40",
  },
};

const FALLBACK_THEME = {
  gradient: "from-neutral-500 to-neutral-700",
  icon: "text-white",
  ring: "ring-neutral-300/40",
};

export function CategoryTiles({ categories }: { categories: CategoryNode[] }) {
  const roots = categories.slice(0, 10);
  if (!roots.length) return null;

  return (
    <section className="py-8">
      <div className="mb-5 flex items-end justify-between">
        <div>
          <h2 className="font-heading text-2xl font-bold text-neutral-900 sm:text-3xl">
            Kategoriyalar
          </h2>
          <p className="mt-1 text-sm text-khaki-700">
            Ehtiyojingizga mos bo&apos;limni tanlang
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {roots.map((cat) => {
          const Icon = categoryIcon(cat.icon || "package");
          const theme = TILE_THEMES[cat.slug] ?? FALLBACK_THEME;
          return (
            <Link
              key={cat.id}
              href={`/catalog?category=${cat.slug}`}
              className={`group relative flex h-[140px] flex-col justify-between overflow-hidden rounded-2xl bg-gradient-to-br ${theme.gradient} p-4 shadow-[var(--shadow-soft)] transition-all hover:-translate-y-1 hover:shadow-[var(--shadow-card)] hover:ring-4 ${theme.ring}`}
            >
              {/* Decorative circle */}
              <span
                aria-hidden
                className="absolute -right-6 -top-6 h-24 w-24 rounded-full bg-white/15 transition-transform group-hover:scale-110"
              />
              <span
                aria-hidden
                className="absolute -bottom-8 -left-8 h-20 w-20 rounded-full bg-white/10"
              />

              {/* Icon */}
              <span className={`relative z-10 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 backdrop-blur ${theme.icon}`}>
                <Icon className="h-5 w-5" />
              </span>

              {/* Text */}
              <div className="relative z-10">
                <p className="font-heading text-lg font-bold text-white drop-shadow-sm">
                  {cat.name}
                </p>
                <p className="mt-0.5 text-xs font-medium text-white/85">
                  {cat.products_count} ta mahsulot
                </p>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
