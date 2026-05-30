import { Link } from "@/i18n/navigation";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-neutral-100 via-neutral-50 to-primary-50 px-4 py-12">
      <Link
        href="/"
        className="mb-8 font-heading text-2xl font-bold text-primary-700"
      >
        My Online Market
      </Link>
      <div className="w-full max-w-md rounded-3xl border border-neutral-200 bg-white p-8 shadow-[var(--shadow-card)]">
        {children}
      </div>
      <Link
        href="/"
        className="mt-6 text-sm text-khaki-600 hover:text-primary-600"
      >
        ← Bosh sahifaga qaytish
      </Link>
    </div>
  );
}
