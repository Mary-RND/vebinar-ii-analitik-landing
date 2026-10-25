import { PlusMark } from "@/components/Medic";

const items = [
  "Маммопластика",
  "Абдоминопластика",
  "Блефаропластика",
  "Ринопластика",
  "Липосакция и контурирование",
  "Гинекомастия",
  "Послеродовое восстановление",
  "Пластика лица и шеи",
];

export function MarqueeStrip() {
  const row = (ariaHidden = false) => (
    <div
      aria-hidden={ariaHidden}
      className="flex shrink-0 items-center gap-8 pr-8"
    >
      {items.map((it) => (
        <span key={it} className="flex items-center gap-8 whitespace-nowrap">
          <span className="font-display text-lg italic text-ivory/70">{it}</span>
          <PlusMark className="text-terracotta/70" />
        </span>
      ))}
    </div>
  );

  return (
    <div
      className="marquee-strip relative overflow-hidden border-y border-ivory/10 bg-graphite py-5"
      style={{
        maskImage:
          "linear-gradient(90deg, transparent, black 8%, black 92%, transparent)",
        WebkitMaskImage:
          "linear-gradient(90deg, transparent, black 8%, black 92%, transparent)",
      }}
    >
      <div className="flex w-max animate-marquee">
        {row()}
        {row(true)}
      </div>
    </div>
  );
}