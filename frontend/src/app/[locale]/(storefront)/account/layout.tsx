"use client";

import { Link, usePathname, useRouter } from "@/i18n/navigation";
import { useEffect } from "react";
import { LogOut, MapPin, Package, User2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth";
import { useLogout } from "@/hooks/useAuth";

const NAV = [
  { href: "/account", label: "Profil", icon: User2 },
  { href: "/account/orders", label: "Buyurtmalar", icon: Package },
  { href: "/account/addresses", label: "Manzillar", icon: MapPin },
];

export default function AccountLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const logout = useLogout();

  // Client-side guard — hydration'dan keyin tekshiriladi
  useEffect(() => {
    const t = setTimeout(() => {
      if (!useAuthStore.getState().isAuthenticated) {
        router.replace("/login");
      }
    }, 300);
    return () => clearTimeout(t);
  }, [router]);

  if (!isAuthenticated) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-20 text-center text-khaki-600">
        Yuklanmoqda...
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[260px_1fr]">
        {/* Sidebar */}
        <aside className="h-fit rounded-2xl border border-neutral-200 bg-white p-4">
          <div className="mb-4 flex items-center gap-3 border-b border-neutral-200 pb-4">
            <div className="grid h-11 w-11 place-items-center rounded-full bg-primary-100 font-heading font-bold text-primary-700">
              {(user?.full_name ?? "U").charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="truncate font-medium text-neutral-900">
                {user?.full_name}
              </p>
              <p className="truncate text-xs text-khaki-600">{user?.email}</p>
            </div>
          </div>

          <nav className="space-y-1">
            {NAV.map((n) => {
              const active =
                pathname === n.href ||
                (n.href !== "/account" && pathname.startsWith(n.href));
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  className={cn(
                    "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors",
                    active
                      ? "bg-primary-50 font-medium text-primary-700"
                      : "text-neutral-700 hover:bg-neutral-100",
                  )}
                >
                  <n.icon className="h-4 w-4" />
                  {n.label}
                </Link>
              );
            })}
            <button
              onClick={() => logout.mutate()}
              className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-primary-600 transition-colors hover:bg-primary-50"
            >
              <LogOut className="h-4 w-4" />
              Chiqish
            </button>
          </nav>
        </aside>

        {/* Content */}
        <div>{children}</div>
      </div>
    </div>
  );
}
