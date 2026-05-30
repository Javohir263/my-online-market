"use client";

import { Link } from "@/i18n/navigation";
import { Heart, LayoutGrid, Package, User2 } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useUIStore } from "@/store/ui";
import { useCategories } from "@/hooks/useCatalog";

const QUICK_LINKS = [
  { href: "/catalog", label: "Katalog", icon: LayoutGrid },
  { href: "/wishlist", label: "Sevimlilar", icon: Heart },
  { href: "/account/orders", label: "Buyurtmalar", icon: Package },
  { href: "/account", label: "Akkaunt", icon: User2 },
];

export function MobileNav() {
  const open = useUIStore((s) => s.mobileMenuOpen);
  const close = useUIStore((s) => s.closeMobileMenu);
  const { data: categories } = useCategories();

  return (
    <Sheet open={open} onOpenChange={(o) => !o && close()}>
      <SheetContent side="left" className="w-full p-0 sm:max-w-xs">
        <SheetHeader className="border-b border-neutral-200 px-5 py-4">
          <SheetTitle className="font-heading text-primary-700">
            My Online Market
          </SheetTitle>
        </SheetHeader>

        <div className="flex flex-col overflow-auto">
          <nav className="grid grid-cols-2 gap-2 p-4">
            {QUICK_LINKS.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                onClick={close}
                className="flex flex-col items-center gap-1.5 rounded-xl border border-neutral-200 p-3 text-center text-xs font-medium text-neutral-700 hover:border-primary-200 hover:bg-primary-50"
              >
                <l.icon className="h-5 w-5 text-primary-600" />
                {l.label}
              </Link>
            ))}
          </nav>

          <div className="px-5 py-2">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-khaki-600">
              Kategoriyalar
            </p>
            <ul className="space-y-0.5 pb-6">
              {categories?.map((cat) => (
                <li key={cat.id}>
                  <Link
                    href={`/catalog?category=${cat.slug}`}
                    onClick={close}
                    className="block rounded-lg px-3 py-2 text-sm text-neutral-700 hover:bg-neutral-100"
                  >
                    {cat.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
