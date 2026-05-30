import { createNavigation } from "next-intl/navigation";
import { routing } from "./routing";

// Locale-aware navigation — bu Link/router URL'ga locale prefix qo'shadi.
export const { Link, redirect, usePathname, useRouter, getPathname } =
  createNavigation(routing);
