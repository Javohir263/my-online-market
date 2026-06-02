import { Link } from "@/i18n/navigation";
import {
  ArrowRight,
  BadgePercent,
  Truck,
  CreditCard,
} from "lucide-react";

const PROMOS = [
  {
    href: "/catalog?is_new=true",
    title: "Yangi kelganlar",
    subtitle: "20% gacha boshlang'ich chegirma",
    icon: BadgePercent,
    gradient: "from-primary-600 to-primary-800",
    accent: "text-gold-400",
    cta: "Ko'rish",
  },
  {
    href: "/help/delivery",
    title: "Bepul yetkazib berish",
    subtitle: "200,000 so'mdan boshlab",
    icon: Truck,
    gradient: "from-accent-600 to-accent-800",
    accent: "text-gold-400",
    cta: "Batafsil",
  },
  {
    href: "/help/payment",
    title: "Click & Payme",
    subtitle: "Tezkor va ishonchli to'lov",
    icon: CreditCard,
    gradient: "from-neutral-700 to-neutral-900",
    accent: "text-gold-400",
    cta: "O'rganish",
  },
];

export function PromoStrip() {
  return (
    <section className="py-7">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {PROMOS.map((p) => (
          <Link
            key={p.title}
            href={p.href}
            className={`group relative flex h-[160px] flex-col justify-between overflow-hidden rounded-2xl bg-gradient-to-br ${p.gradient} p-5 shadow-[var(--shadow-soft)] transition-all hover:-translate-y-1 hover:shadow-[var(--shadow-card)]`}
          >
            {/* Decorative shapes */}
            <span
              aria-hidden
              className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-white/10"
            />
            <span
              aria-hidden
              className="absolute -bottom-10 -left-10 h-24 w-24 rounded-full bg-white/5"
            />

            <p
              className={`relative z-10 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-white/15 backdrop-blur ${p.accent}`}
            >
              <p.icon className="h-5 w-5" />
            </p>

            <div className="relative z-10">
              <h3 className="font-heading text-xl font-bold text-white drop-shadow-sm">
                {p.title}
              </h3>
              <p className="mt-0.5 text-sm text-white/85">{p.subtitle}</p>
              <span
                className={`mt-2 inline-flex items-center gap-1 text-xs font-semibold uppercase tracking-wide ${p.accent} transition-transform group-hover:translate-x-1`}
              >
                {p.cta}
                <ArrowRight className="h-3.5 w-3.5" />
              </span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
