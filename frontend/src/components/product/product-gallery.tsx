"use client";

import Image from "next/image";
import { useState } from "react";
import { cn } from "@/lib/utils";
import type { ProductImage } from "@/types/api";

export function ProductGallery({
  images,
  name,
}: {
  images: ProductImage[];
  name: string;
}) {
  const sorted = [...images].sort(
    (a, b) => Number(b.is_primary) - Number(a.is_primary) || a.order - b.order,
  );
  const [active, setActive] = useState(0);

  if (sorted.length === 0) {
    return (
      <div className="grid aspect-square place-items-center rounded-2xl bg-neutral-100 text-khaki-400">
        Rasm yo&apos;q
      </div>
    );
  }

  return (
    <div className="flex flex-col-reverse gap-3 sm:flex-row">
      {/* Thumbnails */}
      {sorted.length > 1 && (
        <div className="flex gap-2 sm:flex-col">
          {sorted.map((img, i) => (
            <button
              key={img.id}
              onClick={() => setActive(i)}
              className={cn(
                "relative h-16 w-16 overflow-hidden rounded-lg border-2 bg-neutral-100 transition-colors",
                i === active ? "border-primary-500" : "border-transparent",
              )}
            >
              <Image
                src={img.image}
                alt={img.alt_text || name}
                fill
                sizes="64px"
                className="object-cover"
              />
            </button>
          ))}
        </div>
      )}

      {/* Main */}
      <div className="relative aspect-square flex-1 overflow-hidden rounded-2xl border border-neutral-200 bg-neutral-100">
        <Image
          src={sorted[active].image}
          alt={sorted[active].alt_text || name}
          fill
          priority
          sizes="(max-width: 640px) 100vw, 50vw"
          className="object-cover"
        />
      </div>
    </div>
  );
}
