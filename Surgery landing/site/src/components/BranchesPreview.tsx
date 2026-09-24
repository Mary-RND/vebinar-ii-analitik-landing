import Link from "next/link";
import { Reveal } from "@/components/Reveal";

export function BranchesPreview() {
  return (
    <section id="napravleniya" className="bg-sand/40">
      <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
        <Reveal className="mx-auto max-w-2xl text-center">
          <p className="eyebrow text-bronze">Направления</p>
          <h2 className="mt-4 font-display text-3xl font-medium sm:text-5xl">
            Выберите направление
          </h2>
          <p className="mt-4 text-sm text-ink/55">
            Каждая зона — это отдельная история. Нажмите на область, чтобы узнать,
            какие решения возможны именно там.
          </p>
        </Reveal>

        <div className="mt-12 grid gap-6 lg:grid-cols-2">
          <Reveal className="group relative overflow-hidden rounded-[28px] bg-white p-8 shadow-[0_20px_60px_-30px_rgba(42,40,37,0.25)] sm:p-10">
            <div className="absolute inset-0 bg-gradient-to-br from-terracotta/10 via-transparent to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
            <div className="relative">
              <div className="flex items-center gap-3">
                <span className="size-2 rounded-full bg-terracotta" />
                <p className="eyebrow text-terracotta">Женская пластика</p>
              </div>
              <h3 className="mt-4 font-display text-2xl font-medium">
                Женское тело
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-ink/60">
                Грудь · Живот · Бёдра · Ягодицы · Руки · Лицо
              </p>
              <div className="mt-8 flex min-h-[220px] items-center justify-center rounded-2xl bg-marble">
                <p className="px-6 text-center text-sm italic text-ink/40">
                  Интерактивная 3D-карта — женская фигура с подсветкой зон
                  <br />
                  (модуль 3: клик по зоне → мамопластика, абдоминопластика и т.д.)
                </p>
              </div>
              <Link
                href="/#forma"
                className="mt-8 inline-flex items-center gap-2 text-sm font-semibold text-terracotta transition-colors hover:text-bronze"
              >
                Исследовать женские направления
                <span aria-hidden>→</span>
              </Link>
            </div>
          </Reveal>

          <Reveal delay={0.1} className="group relative overflow-hidden rounded-[28px] bg-graphite p-8 text-ivory shadow-[0_20px_60px_-30px_rgba(0,0,0,0.5)] sm:p-10">
            <div className="absolute inset-0 bg-gradient-to-br from-bronze/15 via-transparent to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
            <div className="relative">
              <div className="flex items-center gap-3">
                <span className="size-2 rounded-full bg-bronze" />
                <p className="eyebrow text-bronze">Мужская пластика</p>
              </div>
              <h3 className="mt-4 font-display text-2xl font-medium">
                Мужское тело
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-ivory/60">
                Грудь · Живот · Спина · Лицо · Шея
              </p>
              <p className="mt-2 max-w-md text-sm leading-relaxed text-ivory/55">
                Мужское тело требует другого подхода: другие пропорции, другая эстетика
                результата, другая работа с рубцами. Здесь это учитывается с первого эскиза.
              </p>
              <div className="mt-8 flex min-h-[220px] items-center justify-center rounded-2xl bg-ivory/5 ring-1 ring-ivory/10">
                <p className="px-6 text-center text-sm italic text-ivory/40">
                  Интерактивная 3D-карта — мужская фигура
                  <br />
                  (модуль 3: гинекомастия, ринопластика, липосакция)
                </p>
              </div>
              <Link
                href="/muzhskaya-plastika"
                className="mt-8 inline-flex items-center gap-2 text-sm font-semibold text-bronze transition-colors hover:text-ivory"
              >
                Исследовать мужские направления
                <span aria-hidden>→</span>
              </Link>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}