/**
 * Formatting helpers — narx, sana.
 */

export function formatPrice(
  value: string | number,
  currency = "UZS",
): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  const formatted = new Intl.NumberFormat("uz-UZ", {
    maximumFractionDigits: 0,
  }).format(num);
  return `${formatted} ${currency}`;
}

export function formatDate(iso: string, locale = "uz-UZ"): string {
  return new Intl.DateTimeFormat(locale, {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(iso));
}
