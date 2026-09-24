import { Reveal } from "@/components/Reveal";

const steps = [
  {
    title: "Слушаю.",
    text: "Вы рассказываете, что хотите изменить и почему. Я задаю вопросы — иногда неудобные, но важные.",
  },
  {
    title: "Показываю.",
    text: "На основе анатомии и ваших целей я объясняю, какие варианты существуют, чем они отличаются, какие у каждого ограничения. Без красивых картинок из интернета — только то, что реально достижимо в вашем случае.",
  },
  {
    title: "Решаете вы.",
    text: "Я не уговариваю. Если операция вам не нужна или не подходит — я скажу об этом прямо. Если нужна — вы получите план и время подумать.",
  },
];

export function HowItWorks() {
  return (
    <section id="pervaya-vstrecha" className="bg-sand/35">
      <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
        <Reveal className="mx-auto max-w-2xl text-center">
          <p className="eyebrow text-bronze">Первая встреча</p>
          <h2 className="mt-4 font-display text-3xl font-medium sm:text-5xl">
            Как проходит консультация
          </h2>
        </Reveal>
        <div className="mx-auto mt-12 grid max-w-5xl gap-6 sm:grid-cols-3">
          {steps.map((s, i) => (
            <Reveal key={s.title} delay={i * 0.08} className="rounded-2xl bg-white p-8 shadow-sm ring-1 ring-ink/5">
              <h3 className="font-display text-xl font-medium">{s.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink/65">{s.text}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}