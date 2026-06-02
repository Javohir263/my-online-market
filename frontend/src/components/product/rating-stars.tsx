import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Reyting yulduzlari. Ikkita rejim:
 *   - "full" (default): 5 ta yulduz + sharhlar soni
 *   - "compact": 4.5 ★ (124) — kompakt, kartochka uchun ideal
 */
export function RatingStars({
  value,
  count,
  size = 14,
  showCount = true,
  variant = "full",
}: {
  value: number | string;
  count?: number;
  size?: number;
  showCount?: boolean;
  variant?: "full" | "compact";
}) {
  const rating = typeof value === "string" ? parseFloat(value) : value;

  if (variant === "compact") {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-medium text-neutral-700">
        <Star
          style={{ width: size, height: size }}
          className="fill-gold-500 text-gold-500"
        />
        {rating.toFixed(1)}
        {showCount && count !== undefined && (
          <span className="text-khaki-500">({count})</span>
        )}
      </span>
    );
  }

  const rounded = Math.round(rating);
  return (
    <div className="flex items-center gap-1">
      <div className="flex">
        {[1, 2, 3, 4, 5].map((i) => (
          <Star
            key={i}
            style={{ width: size, height: size }}
            className={cn(
              i <= rounded
                ? "fill-gold-500 text-gold-500"
                : "fill-neutral-200 text-neutral-200",
            )}
          />
        ))}
      </div>
      {showCount && count !== undefined && (
        <span className="text-xs text-khaki-600">({count})</span>
      )}
    </div>
  );
}
