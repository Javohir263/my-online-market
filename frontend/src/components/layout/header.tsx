"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Heart, Menu, Search, ShoppingBag, User2 } from "lucide-react";
import { useState } from "react";
import { Logo } from "./logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useUIStore } from "@/store/ui";
import { useCart } from "@/hooks/useCart";

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
    <header className="sticky top-0 z-40 border-b border-neutral-200 bg-neutral-50/90 backdrop-blur-md">
      {/* Top strip */}
      <div className="hidden md:block border-b border-neutral-200/70 bg-neutral-100/60">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-1.5 text-xs text-khaki-700">
          <span>Butun O&apos;zbekiston bo&apos;ylab yetkazib berish</span>
          <div className="flex items-center gap-4">
            <Link href="/account/orders" className="hover:text-primary-600">
              Buyurtmalarim
            </Link>
            <span className="text-neutral-300">|</span>
            <span>uz / ru / en</span>
          </div>
        </div>
      </div>

      {/* Main bar */}
      <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3">
        <button
          aria-label="Menu"
          onClick={toggleMobileMenu}
          className="md:hidden text-neutral-700"
        >
          <Menu className="h-6 w-6" />
        </button>

        <Logo />

        {/* Search — center, desktop */}
        <form
          onSubmit={onSearch}
          className="relative hidden flex-1 md:block max-w-xl mx-auto"
        >
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Mahsulot qidirish..."
            className="h-10 rounded-full border-neutral-300 bg-white pl-4 pr-11 focus-visible:ring-primary-500"
          />
          <button
            type="submit"
            aria-label="Qidirish"
            className="absolute right-1 top-1 grid h-8 w-8 place-items-center rounded-full bg-primary-500 text-white hover:bg-primary-600 transition-colors"
          >
            <Search className="h-4 w-4" />
          </button>
        </form>

        {/* Icons */}
        <nav className="ml-auto flex items-center gap-1">
          <Link href="/search" aria-label="Qidirish" className="md:hidden">
            <Button variant="ghost" size="icon">
              <Search className="h-5 w-5" />
            </Button>
          </Link>
          <Link href="/wishlist" aria-label="Sevimlilar">
            <Button variant="ghost" size="icon">
              <Heart className="h-5 w-5" />
            </Button>
          </Link>
          <Button
            variant="ghost"
            size="icon"
            className="relative"
            onClick={openCart}
            aria-label="Savat"
          >
            <ShoppingBag className="h-5 w-5" />
            {cartCount > 0 && (
              <span className="absolute -right-0.5 -top-0.5 grid h-4 min-w-4 place-items-center rounded-full bg-primary-500 px-1 text-[10px] font-semibold text-white">
                {cartCount > 99 ? "99+" : cartCount}
              </span>
            )}
          </Button>
          <Link href="/account" aria-label="Akkaunt">
            <Button variant="ghost" size="icon">
              <User2 className="h-5 w-5" />
            </Button>
          </Link>
        </nav>
      </div>
    </header>
  );
}
