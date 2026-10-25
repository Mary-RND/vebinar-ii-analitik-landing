"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Reveal } from "@/components/Reveal";
import { PlusMark } from "@/components/Medic";
import { ZoneFigure, type Zone } from "@/components/three/ZoneFigure";

const zones: Zone[] = [
  { id: "belly", hint: "Живот", label: "Абдоминопластика — диастаз и кожа" },
  { id: "breasts", hint: "Грудь", label: "Маммопластика — форма и объём" },
  { id: "hips", hint: "Бёдра и контур", label: "Липосакция и подтяжка" },
];

const chips = ["Живот", "Грудь", "Бёдра"];

export function PostpartumPreview() {
  const router = useRouter();

  return (
    <section className="aurora relative overflow-hidden bg-marble">
      <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
        <div className="grid items-center gap-10 lg:grid-cols-2">
          <Reveal>
            <p className="eyebrow text-bronze">Послеродовое восстановление</p>
            <h2 className="mt-4 font-display text-3xl font-medium leading-tight sm:text-5xl">
              Вернуться
              <br />
              <span className="text-gold italic">к себе после родов</span>
            </h2>
            <div className="mt-6 max-w-xl space-y-4 text-[1.02rem] leading-relaxed text-ink/75">
              <p>
                Тело после родов — это не «испорченное» тело. Это тело, которое сделало
                огромную работу. Но иногда оно не возвращается к прежнему состоянию само —
                и это нормально.
              </p>
              <p>
                Послеродовая пластика — это не одна операция, а маршрут. Часто он включает
                работу с животом (диастаз, кожа), грудью (форма, объём), бёдрами. Мы
                составляем его вместе, учитывая, кормите ли вы ещё, как давно были роды,
                какие у вас планы на будущее.
              </p>
              <p className="italic text-ink/55">Никто не торопит. Никто не оценивает.</p>
            </div>
            <Link
              href="/poslerodovoe-vosstanovlenie"
              className="btn-shine animate-pulse-glove mt-8 inline-flex items-center gap-2 rounded-full bg-terracotta px-7 py-3.5 text-sm font-semibold text-ivory transition hover:bg-bronze"
            >
              Обсудить маршрут восстановления
              <span aria-hidden>→</span>
            </Link>
          </Reveal>

          <Reveal delay={0.14} className="relative">
            <div
              aria-hidden="true"
              className="animate-float-slow pointer-events-none absolute -left-10 -top-10 size-40 rounded-full bg-terracotta/25 blur-3xl"
            />
            <div
              aria-hidden="true"
              className="animate-float-slow pointer-events-none absolute -bottom-12 -right-8 size-44 rounded-full bg-emerald/20 blur-3xl"
              style={{ animationDelay: "1.6s" }}
            />
            <div className="lift group relative overflow-hidden rounded-[28px] bg-white p-8 shadow-[0_24px_70px_-30px_rgba(42,40,37,0.35)] sm:p-10">
              <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 bg-gradient-to-br from-terracotta/10 via-transparent to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100"
              />
              <p className="relative font-display text-xl font-medium italic text-ink/80">
                Маршрут: живот · грудь · бёдра
              </p>
              <p className="relative mt-1 text-xs text-ink/45">
                Наведите курсор на зону — увидите направление. Нажмите, чтобы открыть
                страницу маршрута.
              </p>
              <div className="relative mt-4 overflow-hidden rounded-2xl bg-marble ring-1 ring-ink/5">
                <ZoneFigure
                  kind="female"
                  accent="#b8734f"
                  zones={zones}
                  className="h-[340px] sm:h-[380px]"
                  onPick={() => router.push("/poslerodovoe-vosstanovlenie")}
                />
              </div>
              <div className="relative mt-4 flex flex-wrap gap-2">
                {chips.map((c) => (
                  <span
                    key={c}
                    className="flex items-center gap-2 rounded-full bg-marble px-4 py-2 text-xs font-medium text-ink/65 ring-1 ring-ink/5"
                  >
                    <PlusMark className="size-4 text-terracotta" />
                    {c}
                  </span>
                ))}
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
