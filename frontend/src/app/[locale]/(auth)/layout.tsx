import { Link } from "@/i18n/navigation";
import { ArrowLeft, ShieldCheck, Sparkles, Truck } from "lucide-react";

const BENEFITS = [
  {
    icon: Truck,
    title: "Tez yetkazib berish",
    text: "Butun O'zbekiston bo'ylab 1-3 kun ichida.",
  },
  {
    icon: ShieldCheck,
    title: "Xavfsiz to'lov",
    text: "Click, Payme va naqd to'lov variantlari.",
  },
  {
    icon: Sparkles,
    title: "Premium kolleksiya",
    text: "543+ noyob mahsulot, tekshirilgan brendlardan.",
  },
];

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[1.05fr_1fr]">
      {/* ─── Left: brand visual panel (desktop only) ─── */}
      <aside className="relative hidden overflow-hidden bg-gradient-to-br from-primary-700 via-primary-600 to-primary-800 lg:flex lg:flex-col lg:justify-between">
        {/* Decorative shapes */}
        <span
          aria-hidden
          className="absolute -right-32 -top-32 h-96 w-96 rounded-full bg-white/8"
        />
        <span
          aria-hidden
          className="absolute -bottom-24 -left-24 h-72 w-72 rounded-full bg-gold-400/15"
        />
        <span
          aria-hidden
          className="absolute right-1/4 top-1/3 h-40 w-40 rounded-full bg-white/5"
        />

        <div className="relative z-10 p-10">
          <Link
            href="/"
            className="inline-flex items-center gap-2 font-heading text-2xl font-bold text-white"
          >
            My Online Market
          </Link>
        </div>

        <div className="relative z-10 p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-gold-400">
            Premium marketplace
          </p>
          <h2 className="mt-3 max-w-md font-heading text-3xl font-bold leading-tight text-white sm:text-4xl">
            Sifat va nafosat — bir joyda
          </h2>
          <p className="mt-3 max-w-md text-sm leading-relaxed text-white/80">
            Akkauntingizga kirib, sevimlilar ro&apos;yxatingizni saqlang,
            buyurtmalaringizni kuzating va shaxsiy tavsiyalar oling.
          </p>

          <ul className="mt-8 space-y-4">
            {BENEFITS.map((b) => (
              <li key={b.title} className="flex items-start gap-3">
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-white/15 text-gold-400 backdrop-blur">
                  <b.icon className="h-5 w-5" />
                </span>
                <div>
                  <p className="font-semibold text-white">{b.title}</p>
                  <p className="mt-0.5 text-sm text-white/75">{b.text}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="relative z-10 p-10">
          <p className="text-xs text-white/60">
            © {new Date().getFullYear()} My Online Market. Barcha huquqlar
            himoyalangan.
          </p>
        </div>
      </aside>

      {/* ─── Right: form card ─── */}
      <main className="flex flex-col bg-neutral-50">
        <div className="flex items-center justify-between p-6 lg:p-8">
          {/* Mobile logo */}
          <Link
            href="/"
            className="font-heading text-xl font-bold text-primary-700 lg:hidden"
          >
            My Online Market
          </Link>
          <Link
            href="/"
            className="ml-auto inline-flex items-center gap-1.5 text-sm text-khaki-700 transition-colors hover:text-primary-600"
          >
            <ArrowLeft className="h-4 w-4" />
            Bosh sahifa
          </Link>
        </div>

        <div className="flex flex-1 items-center justify-center p-6 lg:p-8">
          <div className="w-full max-w-md">{children}</div>
        </div>
      </main>
    </div>
  );
}
