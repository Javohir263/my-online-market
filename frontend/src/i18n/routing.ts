import { defineRouting } from "next-intl/routing";

export const routing = defineRouting({
  locales: ["uz", "ru", "en"],
  defaultLocale: "uz",
  localePrefix: "always", // /uz, /ru, /en — har til alohida URL (SEO + hreflang)
});

export type Locale = (typeof routing.locales)[number];
