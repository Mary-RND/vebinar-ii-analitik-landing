import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Reveal } from "@/components/Reveal";
import { ContactForm } from "@/components/ContactForm";
import Link from "next/link";

export const metadata = {
  title: "Мужская пластика — пластическая хирургия для мужчин",
  description: "Мужская пластика: грудь, живот, спина, лицо и шея. Другая эстетика результата, другая работа с рубцами — с первого эскиза.",
};

const zones = [
  { k: "Грудь", d: "Гинекомастия — коррекция формы грудной клетки, липосакция и иссечение железистой ткани по показаниям." },
  { k: "Живот", d: "Абдоминопластика и липосакция с учётом мужских пропорций и распределения жировой ткани." },
  { k: "Спина и бока", d: "Контурирование, липосакция flank-зон, работа с кожным избытком." },
  { k: "Лицо и шея", d: "Блефаропластика, ринопластика, пластика шеи — сохранение маскулинных черт." },
];

export default function Page() {
  return (
    <>
      <Header />
      <main className="flex-1">
        <section className="bg-graphite pt-28 text-ivory">
          <div className="mx-auto max-w-7xl px-5 pb-16 sm:px-8 sm:pb-20">
            <Reveal>
              <p className="eyebrow text-bronze">Направление</p>
              <h1 className="mt-4 max-w-3xl font-display text-4xl font-medium leading-tight sm:text-6xl">
                Мужская
                <br />
                <span className="italic text-ivory/60">пластика</span>
              </h1>
              <p className="mt-6 max-w-2xl text-[1.02rem] leading-relaxed text-ivory/70">
                Мужское тело требует другого подхода: другие пропорции, другая эстетика
                результата, другая работа с рубцами. Здесь это учитывается с первого эскиза.
                Без гендерных стереотипов — с той же серьёзностью, что и женская пластика.
              </p>
              <Link
                href="#forma-male"
                className="mt-8 inline-flex items-center gap-2 rounded-full border border-ivory/30 px-7 py-3.5 text-sm font-semibold text-ivory hover:bg-ivory hover:text-graphite"
              >
                Задать вопрос о мужской пластике <span aria-hidden>→</span>
              </Link>
            </Reveal>
          </div>
        </section>

        <section className="bg-marble">
          <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 sm:py-20">
            <Reveal className="mx-auto max-w-2xl text-center">
              <h2 className="font-display text-2xl font-medium sm:text-4xl">Направления</h2>
              <p className="mt-3 text-sm text-ink/55">
                Каждое — с отдельной логикой разрезов, реабилитации и ожидаемого результата.
              </p>
            </Reveal>
            <div className="mx-auto mt-10 grid max-w-5xl gap-6 sm:grid-cols-2">
              {zones.map((z, i) => (
                <Reveal key={z.k} delay={i * 0.07} className="rounded-2xl bg-white p-8 ring-1 ring-ink/5">
                  <h3 className="font-display text-lg font-medium">{z.k}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-ink/60">{z.d}</p>
                </Reveal>
              ))}
            </div>
            <Reveal className="mx-auto mt-8 max-w-3xl rounded-2xl bg-white p-6 text-center text-sm leading-relaxed text-ink/60 ring-1 ring-ink/5 sm:p-8">
              На консультации — честный разбор, что достижимо в вашем случае, какие есть
              ограничения и как будет выглядеть восстановление. Если операция не нужна — скажу
              прямо.
            </Reveal>
          </div>
        </section>

        <section id="forma-male" className="bg-graphite text-ivory">
          <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 sm:py-20">
            <div className="grid gap-10 lg:grid-cols-[1.05fr_1.4fr]">
              <Reveal>
                <p className="eyebrow text-bronze">Начать разговор</p>
                <h2 className="mt-4 font-display text-3xl font-medium sm:text-4xl">Задать вопрос</h2>
                <p className="mt-4 text-sm leading-relaxed text-ivory/60">
                  Первая консультация — это знакомство. Без обязательств и давления.
                </p>
              </Reveal>
              <Reveal delay={0.1} className="rounded-[24px] bg-white p-6 text-ink sm:p-10">
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