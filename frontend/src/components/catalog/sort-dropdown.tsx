"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { ChevronDown } from "lucide-react";

const SORT_OPTIONS = [
  { value: "new", label: "Yangi" },
  { value: "popular", label: "Ommabop" },
  { value: "price", label: "Narx: arzondan" },
  { value: "-price", label: "Narx: qimmatdan" },
  { value: "rating", label: "Reyting" },
];

export function SortDropdown() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const current = searchParams.get("sort") ?? "new";

  const onChange = (value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("sort", value);
    params.delete("page");
    router.push(`${pathname}?${params.toString()}`);
  };

  return (
    <div className="relative inline-flex items-center">
      <select
        value={current}
        onChange={(e) => onChange(e.target.value)}
        className="h-9 appearance-none rounded-lg border border-neutral-200 bg-white pl-3 pr-9 text-sm text-neutral-800 focus:border-primary-400 focus:outline-none"
      >
        {SORT_OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
      <ChevronDown className="pointer-events-none absolute right-2 h-4 w-4 text-khaki-500" />
    </div>
  );
}
