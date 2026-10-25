import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Reveal } from "@/components/Reveal";
import { ContactForm } from "@/components/ContactForm";
import { EcgDivider, PlusMark } from "@/components/Medic";
import { ZoneFigure } from "@/components/three/ZoneFigure";
import Link from "next/link";

export const metadata = {
  title: "Послеродовое восстановление — пластическая хирургия",
  description:
    "Послеродовая пластика — это маршрут: живот, грудь, бёдра. Составляем его вместе, без спешки и оценок.",
};

const steps = [
  { title: "Живот", text: "Диастаз, избыток кожи, растяжки — абдоминопластика и липосакция по показаниям." },
  { title: "Грудь", text: "Форма и объём после лактации — маммопластика, подтяжка, коррекция асимметрии." },
  { title: "Бёдра и контур", text: "Липосакция и подтяжка для восстановления силуэта." },
];

const zones = [
  { id: "belly", hint: "Живот", label: "Абдоминопластика — диастаз и кожа" },
  { id: "breasts", hint: "Грудь", label: "Маммопластика — форма и объём" },
  { id: "hips", hint: "Бёдра и контур", label: "Липосакция и подтяжка" },
];

export default function Page() {
  return (
    <>
      <Header />
      <main className="flex-1">
        <section className="bg-marble pt-28">
          <div className="mx-auto max-w-7xl px-5 pb-16 sm:px-8 sm:pb-20">
            <div className="grid items-center gap-10 lg:grid-cols-[1.15fr_1fr]">
              <Reveal>
                <p className="eyebrow text-bronze">Направление</p>
                <h1 className="mt-4 max-w-3xl font-display text-4xl font-medium leading-tight sm:text-6xl">
                  Вернуться
                  <br />
                  <span className="text-gold italic">к себе после родов</span>
                </h1>
                <EcgDivider className="mt-5 text-terracotta/60" />
                <div className="mt-6 max-w-2xl space-y-4 text-[1.02rem] leading-relaxed text-ink/75">
                  <p>
                    Тело после родов — это не «испорченное» тело. Это тело, которое сделало
                    огромную работу. Но иногда оно не возвращается к прежнему состоянию само —
                    и это нормально.
                  </p>
                  <p>
                    Послеродовая пластика — это не одна операция, а маршрут. Часто он включает
                    работу с животом (диастаз, кожа), грудью (форма, объём), бёдрами.
                  </p>
                  <p className="italic text-ink/55">Никто не торопит. Никто не оценивает.</p>
                </div>
                <Link
                  href="#forma-postpartum"
                  className="btn-shine animate-pulse-glove mt-8 inline-flex items-center gap-2 rounded-full bg-terracotta px-7 py-3.5 text-sm font-semibold text-ivory transition hover:bg-bronze"
                >
                  Обсудить маршрут восстановления <span aria-hidden>→</span>
                </Link>
              </Reveal>

              <Reveal delay={0.15}>
                <div className="lift relative overflow-hidden rounded-[24px] bg-white p-6 shadow-[0_24px_70px_-30px_rgba(42,40,37,0.35)] sm:p-8">
                  <div
                    className="pointer-events-none absolute inset-0"
                    style={{
                      background:
                        "radial-gradient(60% 45% at 15% 10%, rgba(184,115,79,0.12), transparent 70%), radial-gradient(50% 45% at 88% 92%, rgba(139,111,71,0.1), transparent 70%)",
                    }}
                  />
                  <p className="relative font-display text-xl font-medium italic text-ink/80">
                    Зоны маршрута
                  </p>
                  <p className="relative mt-1 text-xs text-ink/45">
                    Наведите курсор — увидите возможное направление коррекции
                  </p>
                  <div className="relative mt-4 overflow-hidden rounded-2xl bg-marble">
                    <ZoneFigure
                      kind="female"
                      accent="#b8734f"
                      zones={zones}
                      className="h-[300px] sm:h-[360px]"
                    />
                  </div>
                  <div className="relative mt-4 flex flex-wrap gap-2">
                    {steps.map((s) => (
                      <span
                        key={s.title}
                        className="flex items-center gap-2 rounded-full bg-marble px-4 py-2 text-xs font-medium text-ink/65 ring-1 ring-ink/5"
                      >
                        <PlusMark className="size-4 text-terracotta" />
                        {s.title}
                      </span>
                    ))}
                  </div>
                </div>
              </Reveal>
            </div>
          </div>
        </section>

        <section className="bg-white">
          <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 sm:py-20">
            <Reveal className="mx-auto max-w-2xl text-center">
              <h2 className="font-display text-2xl font-medium sm:text-4xl">Маршрут восстановления</h2>
              <p className="mt-3 text-sm text-ink/55">
                План зависит от ваших целей, сроков после родов и планов на будущее. Ниже —
                типовые направления, которые комбинируются индивидуально.
              </p>
            </Reveal>
            <div className="mx-auto mt-10 grid max-w-5xl gap-6 sm:grid-cols-3">
              {steps.map((s, i) => (
                <Reveal key={s.title} delay={i * 0.07}>
                  <div className="lift group relative h-full overflow-hidden rounded-2xl bg-marble p-8 ring-1 ring-ink/5">
                    <div
                      className="pointer-events-none absolute inset-x-0 top-0 h-px"
                      style={{
                        background:
                          "linear-gradient(90deg, transparent, rgba(184,115,79,0.5), transparent)",
                      }}
                    />
                    <div
                      aria-hidden="true"
                      className="pointer-events-none absolute inset-0 bg-gradient-to-br from-terracotta/10 via-transparent to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100"
                    />
                    <div className="relative flex items-start gap-4">
                      <span className="flex size-9 shrink-0 items-center justify-center rounded-full border border-terracotta/30 text-sm font-semibold text-terracotta">
                        {String(i + 1).padStart(2, "0")}
                      </span>
                      <div>
                        <h3 className="font-display text-lg font-medium">{s.title}</h3>
                        <p className="mt-2 text-sm leading-relaxed text-ink/60">{s.text}</p>
                      </div>
                    </div>
                  </div>
                </Reveal>
              ))}
            </div>
            <Reveal className="mx-auto mt-8 max-w-3xl rounded-2xl bg-sand/40 p-6 text-center text-sm leading-relaxed text-ink/60 sm:p-8">
              На консультации обсуждаем, кормите ли вы ещё, когда были роды, какие у вас планы
              на беременность в будущем, и только после этого предлагаем последовательность
              вмешательств — иногда с паузой в несколько месяцев между этапами.
            </Reveal>
          </div>
        </section>

        <section id="forma-postpartum" className="aurora bg-sand/30">
          <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 sm:py-20">
            <div className="grid gap-10 lg:grid-cols-[1.05fr_1.4fr]">
              <Reveal>
                <p className="eyebrow text-bronze">Начать разговор</p>
                <h2 className="mt-4 font-display text-3xl font-medium sm:text-4xl">
                  Обсудить послеродовое восстановление
                </h2>
                <p className="mt-4 text-sm leading-relaxed text-ink/60">
                  Первая консультация — это знакомство. Без обязательств и давления.
                </p>
              </Reveal>
              <Reveal delay={0.1} className="rounded-[24px] bg-white p-6 shadow-sm ring-1 ring-ink/5 sm:p-10">
                <ContactForm />
              </Reveal>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}