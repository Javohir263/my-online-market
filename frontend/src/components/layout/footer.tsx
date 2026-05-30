import Link from "next/link";

const FOOTER_COLS = [
  {
    title: "Xaridorlarga",
    links: [
      { label: "Qanday buyurtma berish", href: "/help/how-to-order" },
      { label: "Yetkazib berish", href: "/help/delivery" },
      { label: "To'lov", href: "/help/payment" },
      { label: "Qaytarish", href: "/help/returns" },
    ],
  },
  {
    title: "Kompaniya",
    links: [
      { label: "Biz haqimizda", href: "/about" },
      { label: "Vakansiyalar", href: "/careers" },
      { label: "Hamkorlik", href: "/partnership" },
    ],
  },
  {
    title: "Yordam",
    links: [
      { label: "Aloqa", href: "/contact" },
      { label: "Savol-javob", href: "/faq" },
      { label: "Maxfiylik siyosati", href: "/privacy" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="mt-auto border-t border-neutral-200 bg-neutral-100">
      <div className="mx-auto grid max-w-7xl grid-cols-2 gap-8 px-4 py-12 md:grid-cols-4">
        <div className="col-span-2 md:col-span-1">
          <h3 className="font-heading text-lg font-bold text-primary-700">
            My Online Market
          </h3>
          <p className="mt-3 text-sm leading-relaxed text-khaki-700">
            Premium online marketplace — sifatli mahsulotlar, ishonchli
            yetkazib berish.
          </p>
        </div>

        {FOOTER_COLS.map((col) => (
          <div key={col.title}>
            <h4 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-800">
              {col.title}
            </h4>
            <ul className="space-y-2">
              {col.links.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-khaki-700 transition-colors hover:text-primary-600"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="border-t border-neutral-200">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 px-4 py-4 text-xs text-khaki-600 sm:flex-row">
          <span>
            © {new Date().getFullYear()} My Online Market. Barcha huquqlar
            himoyalangan.
          </span>
          <span>To&apos;lov: Click · Payme · Naqd</span>
        </div>
      </div>
    </footer>
  );
}
