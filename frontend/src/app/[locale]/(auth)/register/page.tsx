"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "@/i18n/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useRegister } from "@/hooks/useAuth";

const schema = z
  .object({
    full_name: z.string().min(2, "Ism kamida 2 harf"),
    email: z.string().email("To'g'ri email kiriting"),
    password: z.string().min(8, "Parol kamida 8 belgi"),
    password_confirm: z.string(),
  })
  .refine((d) => d.password === d.password_confirm, {
    message: "Parollar mos kelmaydi",
    path: ["password_confirm"],
  });

type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
  const registerMut = useRegister();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = (data: FormData) => registerMut.mutate(data);

  return (
    <div className="rounded-3xl bg-white p-8 shadow-[var(--shadow-card)] ring-1 ring-neutral-200/60 sm:p-10">
      <div>
        <h1 className="font-heading text-3xl font-bold text-neutral-900">
          Ro&apos;yxatdan o&apos;tish
        </h1>
        <p className="mt-1.5 text-sm text-khaki-700">
          Yangi akkaunt yarating va premium xizmatlarga kirishing.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-7 space-y-4">
        <Field label="To'liq ism" error={errors.full_name?.message}>
          <Input
            placeholder="Ism Familiya"
            autoComplete="name"
            className="h-11"
            {...register("full_name")}
          />
        </Field>
        <Field label="Email" error={errors.email?.message}>
          <Input
            type="email"
            placeholder="siz@email.com"
            autoComplete="email"
            className="h-11"
            {...register("email")}
          />
        </Field>
        <Field label="Parol" error={errors.password?.message}>
          <Input
            type="password"
            placeholder="kamida 8 belgi"
            autoComplete="new-password"
            className="h-11"
            {...register("password")}
          />
        </Field>
        <Field label="Parolni tasdiqlang" error={errors.password_confirm?.message}>
          <Input
            type="password"
            placeholder="••••••••"
            autoComplete="new-password"
            className="h-11"
            {...register("password_confirm")}
          />
        </Field>

        <Button
          type="submit"
          disabled={registerMut.isPending}
          className="h-11 w-full bg-primary-500 text-base font-semibold text-white hover:bg-primary-600"
        >
          {registerMut.isPending ? "Yaratilmoqda..." : "Ro'yxatdan o'tish"}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-khaki-700">
        Akkauntingiz bormi?{" "}
        <Link
          href="/login"
          className="font-semibold text-primary-600 hover:underline"
        >
          Kirish
        </Link>
      </p>
    </div>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-semibold text-neutral-800">
        {label}
      </label>
      {children}
      {error && <p className="mt-1 text-xs text-primary-600">{error}</p>}
    </div>
  );
}
