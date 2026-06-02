"use client";

import { useCallback, useEffect, useState } from "react";
import Image from "next/image";
import { Link } from "@/i18n/navigation";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import { categoryIcon } from "@/lib/category-icon";
import type { Banner, CategoryNode } from "@/types/api";

export function HeroBanner({
  banners,
  categories,
}: {
  banners: Banner[];
  categories: CategoryNode[];
}) {
  const slides = banners ?? [];
  const count = slides.length;
  const [active, setActive] = useState(0);

  const go = useCallback(
    (i: number) => {
      if (count === 0) return;
      setActive((i + count) % count);
    },
    [count],
  );

  useEffect(() => {
    if (count <= 1) return;
    const t = setInterval(() => setActive((a) => (a + 1) % count), 5500);
    return () => clearInterval(t);
  }, [count]);

  const roots = (categories ?? []).slice(0, 9);

  return (
    <section className="pt-4">
      <div className="grid gap-4 lg:grid-cols-[248px_1fr]">
        {/* Category rail (desktop) */}
        <nav className="hidden rounded-2xl border border-neutral-200 bg-white p-2 shadow-[var(--shadow-soft)] lg:block">
          <ul className="flex h-full flex-col justify-between">
            {roots.map((cat) => {
              const Icon = categoryIcon(cat.icon);
              return (
                <li key={cat.id}>
                  <Link
                    href={`/catalog?category=${cat.slug}`}
                    className="group flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm text-neutral-700 transition-colors hover:bg-primary-50 hover:text-primary-700"
                  >
                    <Icon className="h-4 w-4 shrink-0 text-khaki-500 transition-colors group-hover:text-primary-600" />
                    <span className="line-clamp-1">{cat.name}</span>
                    <ArrowRight className="ml-auto h-3.5 w-3.5 shrink-0 opacity-0 transition-opacity group-hover:opacity-100" />
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Carousel */}
        <div className="relative h-[260px] overflow-hidden rounded-2xl bg-neutral-100 sm:h-[330px] lg:h-[400px]">
          {count === 0 ? (
            <div className="flex h-full flex-col items-center justify-center gap-4 bg-gradient-to-br from-primary-700 via-primary-600 to-primary-800 p-8 text-center text-white">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-gold-400">
                Premium marketplace
              </p>
              <h2 className="max-w-md font-heading text-2xl font-bold sm:text-4xl">
                Sifat va nafosat — bir joyda
              </h2>
              <Link
                href="/catalog"
                className="mt-1 inline-flex items-center gap-1.5 rounded-full bg-white px-6 py-2.5 text-sm font-semibold text-primary-700 shadow-lg transition-transform hover:scale-[1.03]"
              >
                Xarid qilish <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          ) : (
            slides.map((b, i) => (
              <div
                key={b.id}
                aria-hidden={i !== active}
                className={`absolute inset-0 transition-opacity duration-700 ${
                  i === active ? "opacity-100" : "pointer-events-none opacity-0"
                }`}
              >
                <Image
                  src={b.image}
                  alt={b.title}
                  fill
                  priority={i === 0}
                  sizes="(max-width: 1024px) 100vw, 70vw"
                  className="object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-r from-primary-900/85 via-primary-900/40 to-transparent" />
                <div className="absolute inset-0 flex flex-col justify-center gap-3 p-6 sm:p-10 lg:p-14">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-gold-400">
                    My Online Market
                  </p>
                  <h2 className="max-w-md font-heading text-2xl font-bold leading-[1.1] text-white sm:text-3xl lg:text-[2.6rem]">
                    {b.title}
                  </h2>
                  {b.subtitle && (
                    <p className="max-w-sm text-sm text-white/85 sm:text-base">
                      {b.subtitle}
                    </p>
                  )}
                  <Link
                    href={b.link || "/catalog"}
                    className="mt-2 inline-flex w-fit items-center gap-1.5 rounded-full bg-white px-6 py-2.5 text-sm font-semibold text-primary-700 shadow-lg transition-transform hover:scale-[1.03]"
                  >
                    Xarid qilish <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            ))
          )}

          {count > 1 && (
            <>
              <button
                type="button"
                aria-label="Oldingi"
                onClick={() => go(active - 1)}
                className="absolute left-3 top-1/2 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-full bg-white/85 text-neutral-800 shadow backdrop-blur transition hover:bg-white"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <button
                type="button"
                aria-label="Keyingi"
                onClick={() => go(active + 1)}
                className="absolute right-3 top-1/2 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-full bg-white/85 text-neutral-800 shadow backdrop-blur transition hover:bg-white"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
              <div className="absolute bottom-4 left-1/2 flex -translate-x-1/2 gap-1.5">
                {slides.map((_, i) => (
                  <button
                    type="button"
                    key={i}
                    aria-label={`Slayd ${i + 1}`}
                    onClick={() => go(i)}
                    className={`h-1.5 rounded-full transition-all ${
                      i === active
                        ? "w-6 bg-white"
                        : "w-1.5 bg-white/60 hover:bg-white/90"
                    }`}
                  />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
