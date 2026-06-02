import { cn } from "@/lib/utils";
import { formatPrice } from "@/lib/format";

/**
 * Commerce-style narx ko'rsatish:
 *  ┌─────────────────────────────┐
 *  │ 13,500,000 UZS    14,500,000│  ← current bold, base struck-through
 *  │ ~1,125,000 so'm/oy          │  ← installment (12 oy) — opt-in
 *  └─────────────────────────────┘
 */
const INSTALLMENT_MIN = 500_000; // shu summadan past mahsulotlarda hint yo'q
const INSTALLMENT_MONTHS = 12;

const SIZES = {
  sm: { current: "text-sm font-bold", base: "text-xs", note: "text-[10px]" },
  md: { current: "text-base font-bold", base: "text-xs", note: "text-[11px]" },
  lg: { current: "text-2xl font-bold", base: "text-sm", note: "text-xs" },
} as const;

export function Price({
  current,
  base,
  currency = "UZS",
  hasDiscount = false,
  size = "md",
  showInstallment = false,
  className,
}: {
  current: string | number;
  base?: string | number;
  currency?: string;
  hasDiscount?: boolean;
  size?: "sm" | "md" | "lg";
  showInstallment?: boolean;
  className?: string;
}) {
  const cls = SIZES[size];
  const currentNum =
    typeof current === "string" ? parseFloat(current) : current;
  const installment = Math.ceil(currentNum / INSTALLMENT_MONTHS);
  const showHint = showInstallment && currentNum >= INSTALLMENT_MIN;

  return (
    <div className={cn("flex flex-col gap-0.5", className)}>
      <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
        <span className={cn("text-neutral-900", cls.current)}>
          {formatPrice(current, currency)}
        </span>
        {hasDiscount && base !== undefined && (
          <span className={cn("text-khaki-500 line-through", cls.base)}>
            {formatPrice(base, currency)}
          </span>
        )}
      </div>
      {showHint && (
        <span className={cn("text-khaki-600", cls.note)}>
          ~{formatPrice(installment, "so'm")}/oy · {INSTALLMENT_MONTHS} oy
        </span>
      )}
    </div>
  );
}
