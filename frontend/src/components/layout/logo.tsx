import Link from "next/link";

export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link
      href="/"
      className={`font-heading text-xl sm:text-2xl font-bold tracking-tight text-primary-700 hover:text-primary-500 transition-colors ${className}`}
    >
      My&nbsp;Online&nbsp;Market
    </Link>
  );
}
