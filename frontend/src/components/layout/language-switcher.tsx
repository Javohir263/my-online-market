"use client";

import { useLocale } from "next-intl";
import { useTransition } from "react";
import { usePathname, useRouter } from "@/i18n/navigation";
import { routing, type Locale } from "@/i18n/routing";
import { cn } from "@/lib/utils";

const LABELS: Record<Locale, string> = {
  uz: "O'z",
  ru: "Ру",
  en: "En",
};

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const switchTo = (next: Locale) => {
    if (next === locale) return;
    startTransition(() => {
      router.replace(pathname, { locale: next });
    });
  };

  return (
    <div
      className={cn(
        "flex items-center gap-0.5 rounded-full border border-neutral-200 bg-white p-0.5",
        isPending && "opacity-60",
      )}
    >
      {routing.locales.map((l) => (
        <button
          key={l}
          onClick={() => switchTo(l)}
          className={cn(
            "rounded-full px-2 py-0.5 text-xs font-medium transition-colors",
            l === locale
              ? "bg-primary-500 text-white"
              : "text-khaki-600 hover:text-primary-600",
          )}
          aria-current={l === locale}
        >
          {LABELS[l]}
        </button>
      ))}
    </div>
  );
}
