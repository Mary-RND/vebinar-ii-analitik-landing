import Link from "next/link";
import { Reveal } from "@/components/Reveal";

export function PostpartumPreview() {
  return (
    <section className="bg-marble">
      <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
        <div className="grid items-center gap-10 lg:grid-cols-2">
          <Reveal>
            <p className="eyebrow text-bronze">Послеродовое восстановление</p>
            <h2 className="mt-4 font-display text-3xl font-medium leading-tight sm:text-5xl">
              Вернуться
              <br />
              <span className="italic text-ink/60">к себе после родов</span>
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
              className="mt-8 inline-flex items-center gap-2 rounded-full bg-terracotta px-7 py-3.5 text-sm font-semibold text-ivory transition hover:bg-bronze"
            >
              Обсудить маршрут восстановления
              <span aria-hidden>→</span>
            </Link>
          </Reveal>
          <Reveal delay={0.14} className="relative">
            <div className="overflow-hidden rounded-[28px] bg-sand p-8 sm:p-10">
              <div className="flex min-h-[360px] flex-col items-center justify-center rounded-2xl bg-white/70 px-6 text-center ring-1 ring-ink/5">
                <p className="font-display text-lg italic text-ink/50">
                  Маршрут: живот · грудь · бёдра
                </p>
                <p className="mt-3 max-w-sm text-sm leading-relaxed text-ink/45">
                  Диастаз, кожа, форма и объём — собираем план вместе, без спешки.
                  Мини-карта тела с зонами коррекции — на странице направления.
                </p>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}