import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  actionHref,
}: {
  icon: LucideIcon;
  title: string;
  description?: string;
  actionLabel?: string;
  actionHref?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-3xl border border-dashed border-neutral-300 bg-neutral-50/50 px-6 py-16 text-center">
      <div className="grid h-16 w-16 place-items-center rounded-2xl bg-primary-50 text-primary-500">
        <Icon className="h-8 w-8" />
      </div>
      <h3 className="mt-5 font-heading text-xl font-semibold text-neutral-900">
        {title}
      </h3>
      {description && (
        <p className="mt-1.5 max-w-sm text-sm text-khaki-700">{description}</p>
      )}
      {actionLabel && actionHref && (
        <Link
          href={actionHref}
          className={cn(
            buttonVariants(),
            "mt-6 h-10 bg-primary-500 px-6 text-white hover:bg-primary-600",
          )}
        >
          {actionLabel}
        </Link>
      )}
    </div>
  );
}
