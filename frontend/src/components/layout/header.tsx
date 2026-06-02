"use client";

import { Link, useRouter } from "@/i18n/navigation";
import { Heart, Menu, Search, ShoppingBag, User2 } from "lucide-react";
import { useState } from "react";
import { Logo } from "./logo";
import { Input } from "@/components/ui/input";
import { useUIStore } from "@/store/ui";
import { useCart } from "@/hooks/useCart";
import { LanguageSwitcher } from "./language-switcher";
import { CatalogMenu } from "./catalog-menu";

export function Header() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const toggleMobileMenu = useUIStore((s) => s.toggleMobileMenu);
  const openCart = useUIStore((s) => s.openCart);
  const { data: cart } = useCart();
  const cartCount = cart?.items_count ?? 0;

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const q = query.trim();
    if (q) router.push(`/search?q=${encodeURIComponent(q)}`);
  };

  return (
    <header className="sticky top-0 z-40 border-b border-neutral-200 bg-neutral-50/95 backdrop-blur-md">
      {/* Top strip */}
      <div className="hidden border-b border-neutral-200/70 bg-neutral-100/70 md:block">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-1.5 text-xs text-khaki-700">
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-accent-500" />
            Butun O&apos;zbekiston bo&apos;ylab tez yetkazib berish
          </span>
          <div className="flex items-center gap-4">
            <Link href="/account/orders" className="hover:text-primary-600">
              Buyurtmalarim
            </Link>
            <Link href="/help/delivery" className="hover:text-primary-600">
              Yordam
            </Link>
            <span className="text-neutral-300">|</span>
            <LanguageSwitcher />
          </div>
        </div>
      </div>

      {/* Main bar */}
      <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-3 lg:gap-5">
        <button
          aria-label="Menyu"
          onClick={toggleMobileMenu}
          className="text-neutral-700 md:hidden"
        >
          <Menu className="h-6 w-6" />
        </button>

        <Logo />

        <CatalogMenu />

        {/* Search — center, desktop */}
        <form onSubmit={onSearch} className="relative hidden flex-1 md:block">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Mahsulot, brend yoki kategoriya qidiring..."
            className="h-11 rounded-xl border-neutral-300 bg-white pl-4 pr-12 text-sm focus-visible:ring-primary-500"
          />
          <button
            type="submit"
            aria-label="Qidirish"
            className="absolute right-1.5 top-1.5 grid h-8 w-9 place-items-center rounded-lg bg-primary-500 text-white transition-colors hover:bg-primary-600"
          >
            <Search className="h-4 w-4" />
          </button>
        </form>

        {/* Actions */}
        <nav className="ml-auto flex items-center gap-0.5 sm:gap-1">
          <Link
            href="/search"
            aria-label="Qidirish"
            className="grid h-10 w-10 place-items-center rounded-lg text-neutral-700 hover:bg-neutral-100 md:hidden"
          >
            <Search className="h-5 w-5" />
          </Link>

          <Link
            href="/wishlist"
            aria-label="Sevimlilar"
            className="flex flex-col items-center gap-0.5 rounded-lg px-2.5 py-1 text-[11px] font-medium text-neutral-600 transition-colors hover:bg-neutral-100 hover:text-primary-600"
          >
            <Heart className="h-5 w-5" />
            <span className="hidden md:block">Sevimlilar</span>
          </Link>

          <button
            type="button"
            onClick={openCart}
            aria-label="Savat"
            className="flex flex-col items-center gap-0.5 rounded-lg px-2.5 py-1 text-[11px] font-medium text-neutral-600 transition-colors hover:bg-neutral-100 hover:text-primary-600"
          >
            <span className="relative">
              <ShoppingBag className="h-5 w-5" />
              {cartCount > 0 && (
                <span className="absolute -right-2 -top-1.5 grid h-4 min-w-4 place-items-center rounded-full bg-primary-500 px-1 text-[10px] font-semibold text-white">
                  {cartCount > 99 ? "99+" : cartCount}
                </span>
              )}
            </span>
            <span className="hidden md:block">Savat</span>
          </button>

          <Link
            href="/account"
            aria-label="Akkaunt"
            className="flex flex-col items-center gap-0.5 rounded-lg px-2.5 py-1 text-[11px] font-medium text-neutral-600 transition-colors hover:bg-neutral-100 hover:text-primary-600"
          >
            <User2 className="h-5 w-5" />
            <span className="hidden md:block">Akkaunt</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}
