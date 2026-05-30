import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";

export default createMiddleware(routing);

export const config = {
  // API, static, va fayllardan tashqari hammasi
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
