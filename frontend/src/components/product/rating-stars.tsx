import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

export function RatingStars({
  value,
  count,
  size = 14,
  showCount = true,
}: {
  value: number | string;
  count?: number;
  size?: number;
  showCount?: boolean;
}) {
  const rating = typeof value === "string" ? parseFloat(value) : value;
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
