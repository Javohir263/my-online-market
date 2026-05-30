"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "@/i18n/navigation";
import { toast } from "sonner";
import { authApi } from "@/lib/api/endpoints";
import { useAuthStore } from "@/store/auth";

export function useLogin() {
  const setUser = useAuthStore((s) => s.setUser);
  const qc = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: authApi.login,
    onSuccess: (user) => {
      setUser(user);
      qc.invalidateQueries({ queryKey: ["cart"] });
      qc.invalidateQueries({ queryKey: ["wishlist"] });
      toast.success(`Xush kelibsiz, ${user.full_name}!`);
      router.push("/account");
    },
    onError: () => toast.error("Email yoki parol noto'g'ri"),
  });
}

export function useRegister() {
  const router = useRouter();
  return useMutation({
    mutationFn: authApi.register,
    onSuccess: () => {
      toast.success("Ro'yxatdan o'tdingiz! Endi tizimga kiring.");
      router.push("/login");
    },
    onError: (err: unknown) => {
      const msg = extractError(err);
      toast.error(msg ?? "Ro'yxatdan o'tishda xatolik");
    },
  });
}

export function useLogout() {
  const clear = useAuthStore((s) => s.clear);
  const qc = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      clear();
      qc.clear();
      toast.success("Tizimdan chiqdingiz");
      router.push("/");
    },
  });
}

function extractError(err: unknown): string | null {
  if (
    typeof err === "object" &&
    err !== null &&
    "response" in err &&
    typeof (err as { response?: unknown }).response === "object"
  ) {
    const data = (err as { response?: { data?: Record<string, unknown> } })
      .response?.data;
    if (data) {
      const first = Object.values(data)[0];
      if (Array.isArray(first) && typeof first[0] === "string") return first[0];
      if (typeof data.detail === "string") return data.detail;
    }
  }
  return null;
}
