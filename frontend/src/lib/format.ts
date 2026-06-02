/**
 * Formatting helpers — narx, sana.
 */

export function formatPrice(
  value: string | number,
  currency = "UZS",
): string {
  // Deterministik formatlash — `Intl.NumberFormat("uz-UZ")` server (Node ICU)
  // va brauzerda farqli ajratuvchi (vergul vs NBSP) qaytaradi → SSR hydration
  // mismatch. Shu sababli oddiy 3-raqamli guruh va probel ishlatamiz.
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (!Number.isFinite(num)) return `0 ${currency}`;
  const intPart = Math.round(num).toString();
  // 1234567 → 1 234 567 (regex har 3 raqam orasiga probel qo'shadi)
  const grouped = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  return `${grouped} ${currency}`;
}

export function formatDate(iso: string, locale = "uz-UZ"): string {
  return new Intl.DateTimeFormat(locale, {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(iso));
}
