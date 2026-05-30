"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { accountsApi } from "@/lib/api/endpoints";
import { useAuthStore } from "@/store/auth";
import type { Language } from "@/types/api";

interface ProfileForm {
  full_name: string;
  phone: string;
  language: Language;
}

export default function ProfilePage() {
  const setUser = useAuthStore((s) => s.setUser);
  const qc = useQueryClient();
  const { data: profile } = useQuery({
    queryKey: ["profile"],
    queryFn: accountsApi.profile,
  });

  const { register, handleSubmit, reset } = useForm<ProfileForm>();

  useEffect(() => {
    if (profile) {
      reset({
        full_name: profile.full_name,
        phone: profile.phone,
        language: profile.language,
      });
    }
  }, [profile, reset]);

  const update = useMutation({
    mutationFn: accountsApi.updateProfile,
    onSuccess: (user) => {
      setUser(user);
      qc.invalidateQueries({ queryKey: ["profile"] });
      toast.success("Profil yangilandi");
    },
    onError: () => toast.error("Xatolik yuz berdi"),
  });

  return (
    <div>
      <h1 className="font-heading text-2xl font-bold text-neutral-900">
        Profil
      </h1>

      <form
        onSubmit={handleSubmit((d) => update.mutate(d))}
        className="mt-6 max-w-lg space-y-4 rounded-2xl border border-neutral-200 bg-white p-6"
      >
        <div>
          <label className="mb-1.5 block text-sm font-medium text-neutral-800">
            Email
          </label>
          <Input value={profile?.email ?? ""} disabled className="bg-neutral-100" />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-neutral-800">
            To&apos;liq ism
          </label>
          <Input {...register("full_name")} />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-neutral-800">
            Telefon
          </label>
          <Input placeholder="+998901234567" {...register("phone")} />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-neutral-800">
            Til
          </label>
          <select
            {...register("language")}
            className="h-9 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm focus:border-primary-400 focus:outline-none"
          >
            <option value="uz">O&apos;zbek</option>
            <option value="ru">Русский</option>
            <option value="en">English</option>
          </select>
        </div>

        <Button
          type="submit"
          disabled={update.isPending}
          className="bg-primary-500 text-white hover:bg-primary-600"
        >
          {update.isPending ? "Saqlanmoqda..." : "Saqlash"}
        </Button>
      </form>
    </div>
  );
}
