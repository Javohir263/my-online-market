import * as Icons from "lucide-react";
import type { ComponentType } from "react";

type IconComp = ComponentType<{ className?: string }>;

/**
 * Backend kategoriya `icon` nomini (kebab-case) lucide-react komponentiga
 * aylantiradi. Topilmasa — Package fallback.
 */
export function categoryIcon(name?: string | null): IconComp {
  const pascal = (name || "package")
    .split("-")
    .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
    .join("");
  const Comp = (Icons as Record<string, unknown>)[pascal] as IconComp | undefined;
  return Comp ?? (Icons.Package as IconComp);
}
