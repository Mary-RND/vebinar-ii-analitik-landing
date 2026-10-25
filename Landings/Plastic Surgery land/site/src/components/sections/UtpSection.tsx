import { Reveal } from "@/components/Reveal";
import { clinics, surgeon } from "@/lib/site";

const pillars = [
  {
    n: "01",
    title: "Один хирург",
    text: `${surgeon.name}, ${surgeon.experience} лет практики. Ведёт лично: от первой консультации до контрольного осмотра через три месяца.`,
  },
  {
    n: "02",
    title: "Одна бригада",
    text: "Анестезиолог, ассистент, операционная сестра и координатор работают постоянно. Вы знаете, кто будет рядом.",
  },
  {
    n: "03",
    title: "Четыре клиники",
    text: `${clinics.length} адреса в Москве и Подмосковье. Меняется адрес — не меняются хирург, протокол и оснащение.`,
  },
  {
    n: "04",
    title: "Одна методика",
    text: "Одинаковый протокол и одни и те же материалы в каждой клинике. Результат не зависит от того, куда вы приехали.",
  },
];

export function UtpSection() {
  return (
    <section id="utp" className="relative overflow-hidden bg-paper py-14 sm:py-20">
      <div className="absolute inset-0 aurora opacity-70" aria-hidden="true" />

      <div className="relative mx-auto max-w-7xl px-5 sm:px-8">
        <Reveal className="max-w-3xl">
          <p className="eyebrow text-indigo">Позиционирование</p>
          <h2 className="mt-5 font-display text-4xl font-medium leading-tight sm:text-5xl">
            Четыре обещания, которые можно проверить
          </h2>
          <p className="mt-6 text-lg leading-relaxed text-slate">
            У пластического хирурга легко потеряться: клиники, кабинеты,
            «партнёры», скидки. Здесь всё устроено проще — один человек ведёт
            случай от начала до конца, и вокруг него фиксированная команда.
          </p>
        </Reveal>

        <div className="mt-10 grid gap-px overflow-hidden rounded-3xl bg-ink/10 sm:grid-cols-2 lg:grid-cols-4">
          {pillars.map((p, i) => (
            <Reveal key={p.n} delay={i * 0.08} className="h-full">
              <article className="lift flex h-full flex-col bg-paper p-8">
                <span className="font-display text-5xl font-semibold text-mist">
                  {p.n}
                </span>
                <h3 className="mt-6 font-display text-2xl font-semibold">
                  {p.title}
                </h3>
                <p className="mt-4 text-[0.95rem] leading-relaxed text-slate">
                  {p.text}
                </p>
              </article>
            </Reveal>
          ))}
        </div>

        <Reveal className="mt-12">
          <div className="marquee-strip overflow-hidden rounded-2xl border border-ink/8 bg-fog py-4">
            <div className="flex w-max animate-marquee gap-10 pr-10">
              {[...clinics, ...clinics].map((c, i) => (
                <span
                  key={`${c.id}-${i}`}
                  className="whitespace-nowrap text-sm font-semibold uppercase tracking-[0.2em] text-ink/45"
                >
                  {c.name} · {c.address}
                </span>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}