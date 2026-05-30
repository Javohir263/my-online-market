"use client";

import { Heart } from "lucide-react";
import { ProductCard } from "@/components/product/product-card";
import { ProductCardSkeleton } from "@/components/product/product-card";
import { Breadcrumbs } from "@/components/ui/breadcrumbs";
import { EmptyState } from "@/components/ui/empty-state";
import { useWishlist } from "@/hooks/useWishlist";
import { useAuthStore } from "@/store/auth";

export default function WishlistPage() {
  const isAuth = useAuthStore((s) => s.isAuthenticated);
  const { data: items, isLoading } = useWishlist();

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <Breadcrumbs
        items={[{ label: "Bosh sahifa", href: "/" }, { label: "Sevimlilar" }]}
      />
      <h1 className="mt-4 font-heading text-3xl font-bold text-neutral-900">
        Sevimlilar
      </h1>

      {!isAuth ? (
        <div className="mt-8">
          <EmptyState
            icon={Heart}
            title="Tizimga kiring"
            description="Sevimli mahsulotlaringizni ko'rish uchun akkauntingizga kiring."
            actionLabel="Kirish"
            actionHref="/login"
          />
        </div>
      ) : isLoading ? (
        <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <ProductCardSkeleton key={i} />
          ))}
        </div>
      ) : !items || items.length === 0 ? (
        <div className="mt-8">
          <EmptyState
            icon={Heart}
            title="Sevimlilar bo'sh"
            description="Yoqqan mahsulotlarni ❤️ bosib saqlang."
            actionLabel="Katalogga o'tish"
            actionHref="/catalog"
          />
        </div>
      ) : (
        <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          {items.map((entry, i) => (
            <ProductCard key={entry.id} product={entry.product} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
