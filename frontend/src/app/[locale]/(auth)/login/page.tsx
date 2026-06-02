"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "@/i18n/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useLogin } from "@/hooks/useAuth";

const schema = z.object({
  email: z.string().email("To'g'ri email kiriting"),
  password: z.string().min(1, "Parol kiriting"),
});

type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const login = useLogin();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = (data: FormData) => login.mutate(data);

  return (
    <div className="rounded-3xl bg-white p-8 shadow-[var(--shadow-card)] ring-1 ring-neutral-200/60 sm:p-10">
      <div>
        <h1 className="font-heading text-3xl font-bold text-neutral-900">
          Tizimga kirish
        </h1>
        <p className="mt-1.5 text-sm text-khaki-700">
          Akkauntingizga kiring va xaridni davom ettiring.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-7 space-y-4">
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
            placeholder="••••••••"
            autoComplete="current-password"
            className="h-11"
            {...register("password")}
          />
        </Field>

        <Button
          type="submit"
          disabled={login.isPending}
          className="h-11 w-full bg-primary-500 text-base font-semibold text-white hover:bg-primary-600"
        >
          {login.isPending ? "Kirilmoqda..." : "Kirish"}
        </Button>
      </form>

      <div className="mt-6 rounded-xl bg-neutral-50 p-3 text-xs text-khaki-700">
        <p className="font-semibold text-neutral-800">Demo akkaunt:</p>
        <p className="mt-0.5">
          Email: <code className="text-primary-700">demo@demo.uz</code>
          <span className="mx-2 text-khaki-300">·</span>
          Parol: <code className="text-primary-700">Demo1234!</code>
        </p>
      </div>

      <p className="mt-6 text-center text-sm text-khaki-700">
        Akkauntingiz yo&apos;qmi?{" "}
        <Link
          href="/register"
          className="font-semibold text-primary-600 hover:underline"
        >
          Ro&apos;yxatdan o&apos;ting
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
