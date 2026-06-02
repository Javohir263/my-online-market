import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  output: "standalone", // Docker uchun minimal server bundle
  images: {
    // Lokal Django media (dev) + production CDN'lar.
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/media/**" },
      { protocol: "http", hostname: "127.0.0.1", port: "8000", pathname: "/media/**" },
      { protocol: "https", hostname: "res.cloudinary.com", pathname: "/**" },
      { protocol: "https", hostname: "picsum.photos", pathname: "/**" },
      { protocol: "https", hostname: "fastly.picsum.photos", pathname: "/**" },
      { protocol: "https", hostname: "loremflickr.com", pathname: "/**" },
    ],
    // Dev'da rasm optimizatsiyasini chetlab o'tamiz — Turbopack image
    // optimizer Next 16 da remotePatterns bilan no'noqlikni keltirib chiqaradi
    // ("url parameter is not allowed" 400 xatosi). Production'da Cloudinary
    // o'zi optimizatsiya qiladi.
    unoptimized: process.env.NODE_ENV !== "production",
  },
};

export default withNextIntl(nextConfig);
