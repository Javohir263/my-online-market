import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  output: "standalone", // Docker uchun minimal server bundle
  images: {
    remotePatterns: [
      // Local Django media (dev)
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/media/**" },
      { protocol: "http", hostname: "127.0.0.1", port: "8000", pathname: "/media/**" },
      // Cloudinary (prod)
      { protocol: "https", hostname: "res.cloudinary.com", pathname: "/**" },
      // Picsum (demo seed images)
      { protocol: "https", hostname: "picsum.photos", pathname: "/**" },
      { protocol: "https", hostname: "fastly.picsum.photos", pathname: "/**" },
    ],
  },
};

export default withNextIntl(nextConfig);
