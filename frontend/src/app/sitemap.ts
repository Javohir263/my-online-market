import type { MetadataRoute } from "next";
import { serverCatalog, safe } from "@/lib/api/server";
import { routing } from "@/i18n/routing";

const SITE = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

function localizedAlternates(path: string) {
  const languages: Record<string, string> = {};
  for (const loc of routing.locales) {
    languages[loc] = `${SITE}/${loc}${path}`;
  }
  return languages;
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const staticPaths = ["", "/catalog", "/wishlist", "/login", "/register"];

  const entries: MetadataRoute.Sitemap = staticPaths.map((p) => ({
    url: `${SITE}/${routing.defaultLocale}${p}`,
    lastModified: new Date(),
    changeFrequency: "daily",
    priority: p === "" ? 1 : 0.7,
    alternates: { languages: localizedAlternates(p) },
  }));

  // Dynamic: products
  const products = await safe(
    () => serverCatalog.products({ page_size: 200 }),
    { count: 0, next: null, previous: null, results: [] },
  );
  for (const p of products.results) {
    entries.push({
      url: `${SITE}/${routing.defaultLocale}/product/${p.slug}`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.8,
      alternates: {
        languages: localizedAlternates(`/product/${p.slug}`),
      },
    });
  }

  // Dynamic: categories
  const categories = await safe(serverCatalog.categoryTree, []);
  const flat = (nodes: typeof categories): typeof categories =>
    nodes.flatMap((n) => [n, ...flat(n.children ?? [])]);
  for (const c of flat(categories)) {
    entries.push({
      url: `${SITE}/${routing.defaultLocale}/catalog?category=${c.slug}`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.6,
    });
  }

  return entries;
}
