"use client";

import { useEffect } from "react";
import { authApi } from "@/lib/api/endpoints";
import { useAuthStore } from "@/store/auth";

/**
 * Sahifa yuklanganda /auth/me/ chaqirib, auth store'ni sinxronlaydi.
 * Cookie mavjud bo'lsa user qaytadi; bo'lmasa store tozalanadi.
 */
export function AuthBootstrap() {
  const setUser = useAuthStore((s) => s.setUser);

  useEffect(() => {
    let active = true;
    authApi
      .me()
      .then((user) => active && setUser(user))
      .catch(() => active && setUser(null));
    return () => {
      active = false;
    };
  }, [setUser]);

  return null;
}
