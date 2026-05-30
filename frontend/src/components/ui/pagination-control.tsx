"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

export function PaginationControl({
  page,
  pageSize,
  total,
  onPageChange,
}: {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  if (totalPages <= 1) return null;

  const pages = pageWindow(page, totalPages);

  return (
    <div className="flex items-center justify-center gap-1">
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="grid h-9 w-9 place-items-center rounded-lg border border-neutral-200 text-neutral-700 disabled:opacity-40 hover:border-primary-300 hover:text-primary-600 transition-colors"
        aria-label="Oldingi"
      >
        <ChevronLeft className="h-4 w-4" />
      </button>

      {pages.map((p, i) =>
        p === "..." ? (
          <span key={`e${i}`} className="px-2 text-khaki-500">
            …
          </span>
        ) : (
          <button
            key={p}
            onClick={() => onPageChange(p as number)}
            className={cn(
              "h-9 min-w-9 rounded-lg border px-3 text-sm transition-colors",
              p === page
                ? "border-primary-500 bg-primary-500 text-white"
                : "border-neutral-200 text-neutral-700 hover:border-primary-300 hover:text-primary-600",
            )}
          >
            {p}
          </button>
        ),
      )}

      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        className="grid h-9 w-9 place-items-center rounded-lg border border-neutral-200 text-neutral-700 disabled:opacity-40 hover:border-primary-300 hover:text-primary-600 transition-colors"
        aria-label="Keyingi"
      >
        <ChevronRight className="h-4 w-4" />
      </button>
    </div>
  );
}

function pageWindow(current: number, total: number): (number | "...")[] {
  const delta = 1;
  const range: (number | "...")[] = [];
  const left = Math.max(2, current - delta);
  const right = Math.min(total - 1, current + delta);

  range.push(1);
  if (left > 2) range.push("...");
  for (let i = left; i <= right; i++) range.push(i);
  if (right < total - 1) range.push("...");
  if (total > 1) range.push(total);

  return range;
}
