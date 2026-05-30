"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { PaginationControl } from "@/components/ui/pagination-control";

export function CatalogPagination({
  page,
  pageSize,
  total,
}: {
  page: number;
  pageSize: number;
  total: number;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const onPageChange = (next: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(next));
    router.push(`${pathname}?${params.toString()}`);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <PaginationControl
      page={page}
      pageSize={pageSize}
      total={total}
      onPageChange={onPageChange}
    />
  );
}
