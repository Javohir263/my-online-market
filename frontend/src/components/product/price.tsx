import { cn } from "@/lib/utils";
import { formatPrice } from "@/lib/format";

export function Price({
  current,
  base,
  currency = "UZS",
  hasDiscount = false,
  size = "md",
  className,
}: {
  current: string | number;
  base?: string | number;
  currency?: string;
  hasDiscount?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  const sizes = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-2xl",
  };

  return (
    <div className={cn("flex flex-wrap items-baseline gap-2", className)}>
      <span className={cn("font-semibold text-neutral-900", sizes[size])}>
        {formatPrice(current, currency)}
      </span>
      {hasDiscount && base !== undefined && (
        <span className="text-sm text-khaki-500 line-through">
          {formatPrice(base, currency)}
        </span>
      )}
    </div>
  );
}
