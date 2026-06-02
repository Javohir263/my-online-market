import { Truck, RotateCcw, ShieldCheck } from "lucide-react";

const SIGNALS = [
  {
    icon: Truck,
    title: "Tez yetkazib berish",
    text: "1-3 kun ichida. Toshkentda — kechqurun.",
  },
  {
    icon: RotateCcw,
    title: "14 kun qaytarish",
    text: "Sotib olganingiz yoqmadimi — qaytaring.",
  },
  {
    icon: ShieldCheck,
    title: "Rasmiy kafolat",
    text: "Original mahsulot va to'lov xavfsizligi.",
  },
];

export function TrustSignals() {
  return (
    <ul className="grid grid-cols-1 divide-y divide-neutral-200 overflow-hidden rounded-xl border border-neutral-200 bg-white">
      {SIGNALS.map((s) => (
        <li key={s.title} className="flex items-start gap-3 p-4">
          <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-accent-700/10 text-accent-700">
            <s.icon className="h-4 w-4" />
          </span>
          <div>
            <p className="text-sm font-semibold text-neutral-900">{s.title}</p>
            <p className="mt-0.5 text-xs leading-relaxed text-khaki-700">
              {s.text}
            </p>
          </div>
        </li>
      ))}
    </ul>
  );
}
