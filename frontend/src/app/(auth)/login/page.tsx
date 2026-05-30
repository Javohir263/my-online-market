"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
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
    <div>
      <h1 className="font-heading text-2xl font-bold text-neutral-900">
        Tizimga kirish
      </h1>
      <p className="mt-1 text-sm text-khaki-600">
        Akkauntingizga kiring va xaridni davom ettiring.
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
        <Field label="Email" error={errors.email?.message}>
          <Input
            type="email"
            placeholder="siz@email.com"
            {...register("email")}
          />
        </Field>
        <Field label="Parol" error={errors.password?.message}>
          <Input type="password" placeholder="••••••••" {...register("password")} />
        </Field>

        <Button
          type="submit"
          disabled={login.isPending}
          className="w-full bg-primary-500 text-white hover:bg-primary-600"
        >
          {login.isPending ? "Kirilmoqda..." : "Kirish"}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-khaki-600">
        Akkauntingiz yo&apos;qmi?{" "}
        <Link
          href="/register"
          className="font-medium text-primary-600 hover:underline"
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
      <label className="mb-1.5 block text-sm font-medium text-neutral-800">
        {label}
      </label>
      {children}
      {error && <p className="mt-1 text-xs text-primary-600">{error}</p>}
    </div>
  );
}
