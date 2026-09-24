import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Reveal } from "@/components/Reveal";
import { ContactForm } from "@/components/ContactForm";
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

export default function Page() {
  return (
    <>
      <Header />
      <main className="flex-1">
        <section className="bg-marble pt-28">
          <div className="mx-auto max-w-7xl px-5 pb-16 sm:px-8 sm:pb-20">
            <Reveal>
              <p className="eyebrow text-bronze">Направление</p>
              <h1 className="mt-4 max-w-3xl font-display text-4xl font-medium leading-tight sm:text-6xl">
                Вернуться
                <br />
                <span className="italic text-ink/60">к себе после родов</span>
              </h1>
              <div className="mt-6 max-w-2xl space-y-4 text-[1.02rem] leading-relaxed text-ink/75">
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
                href="#forma-postpartum"
                className="mt-8 inline-flex items-center gap-2 rounded-full bg-terracotta px-7 py-3.5 text-sm font-semibold text-ivory hover:bg-bronze"
              >
                Обсудить маршрут восстановления <span aria-hidden>→</span>
              </Link>
            </Reveal>
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
                <Reveal key={s.title} delay={i * 0.07} className="rounded-2xl bg-marble p-8 ring-1 ring-ink/5">
                  <h3 className="font-display text-lg font-medium">{s.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-ink/60">{s.text}</p>
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

        <section id="forma-postpartum" className="bg-sand/30">
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