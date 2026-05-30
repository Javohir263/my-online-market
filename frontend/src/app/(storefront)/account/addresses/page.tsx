"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { MapPin, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { EmptyState } from "@/components/ui/empty-state";
import { accountsApi, type Address } from "@/lib/api/endpoints";

interface AddrForm {
  recipient_name: string;
  recipient_phone: string;
  region: string;
  city: string;
  street: string;
  building: string;
  apartment: string;
}

export default function AddressesPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { data: addresses, isLoading } = useQuery({
    queryKey: ["addresses"],
    queryFn: accountsApi.addresses,
  });

  const { register, handleSubmit, reset } = useForm<AddrForm>();

  const create = useMutation({
    mutationFn: (data: AddrForm) =>
      accountsApi.createAddress({ ...data, type: "shipping" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["addresses"] });
      toast.success("Manzil qo'shildi");
      setOpen(false);
      reset();
    },
    onError: () => toast.error("Xatolik — barcha maydonlarni to'ldiring"),
  });

  const remove = useMutation({
    mutationFn: (id: number) => accountsApi.deleteAddress(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["addresses"] });
      toast.success("O'chirildi");
    },
  });

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="font-heading text-2xl font-bold text-neutral-900">
          Manzillar
        </h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger
            render={
              <Button className="bg-primary-500 text-white hover:bg-primary-600">
                <Plus className="mr-1 h-4 w-4" />
                Qo&apos;shish
              </Button>
            }
          />
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="font-heading">Yangi manzil</DialogTitle>
            </DialogHeader>
            <form
              onSubmit={handleSubmit((d) => create.mutate(d))}
              className="space-y-3"
            >
              <Input placeholder="Qabul qiluvchi ism" {...register("recipient_name", { required: true })} />
              <Input placeholder="+998901234567" {...register("recipient_phone", { required: true })} />
              <div className="grid grid-cols-2 gap-3">
                <Input placeholder="Viloyat" {...register("region", { required: true })} />
                <Input placeholder="Shahar" {...register("city", { required: true })} />
              </div>
              <Input placeholder="Ko'cha" {...register("street", { required: true })} />
              <div className="grid grid-cols-2 gap-3">
                <Input placeholder="Uy" {...register("building", { required: true })} />
                <Input placeholder="Xonadon" {...register("apartment")} />
              </div>
              <Button
                type="submit"
                disabled={create.isPending}
                className="w-full bg-primary-500 text-white hover:bg-primary-600"
              >
                {create.isPending ? "Saqlanmoqda..." : "Saqlash"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {[1, 2].map((i) => (
            <div key={i} className="h-32 animate-pulse rounded-xl bg-neutral-100" />
          ))}
        </div>
      ) : !addresses || addresses.length === 0 ? (
        <div className="mt-6">
          <EmptyState
            icon={MapPin}
            title="Manzillar yo'q"
            description="Yetkazib berish uchun manzil qo'shing."
          />
        </div>
      ) : (
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {addresses.map((a: Address) => (
            <div
              key={a.id}
              className="rounded-2xl border border-neutral-200 bg-white p-5"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-primary-500" />
                  <span className="font-medium text-neutral-900">
                    {a.recipient_name}
                  </span>
                </div>
                <button
                  onClick={() => remove.mutate(a.id)}
                  className="text-khaki-400 hover:text-primary-600"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              <p className="mt-2 text-sm text-khaki-700">
                {a.recipient_phone}
                <br />
                {[a.region, a.city, a.street, a.building, a.apartment]
                  .filter(Boolean)
                  .join(", ")}
              </p>
              {a.is_default && (
                <span className="mt-2 inline-block rounded-full bg-accent-700/10 px-2 py-0.5 text-xs text-accent-700">
                  Asosiy
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
