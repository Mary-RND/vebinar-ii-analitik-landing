import { Reveal } from "@/components/Reveal";
import { EcgDivider } from "@/components/Medic";

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
          <div className="mt-5 flex justify-center">
            <EcgDivider className="text-terracotta/60" />
          </div>
        </Reveal>
        <div className="mx-auto mt-12 grid max-w-5xl gap-6 sm:grid-cols-3">
          {steps.map((s, i) => (
            <Reveal
              key={s.title}
              delay={i * 0.08}
              className="relative overflow-hidden rounded-2xl bg-white p-8 shadow-sm ring-1 ring-ink/5"
            >
              <div
                className="pointer-events-none absolute inset-x-0 top-0 h-px"
                style={{
                  background:
                    i === 2
                      ? "linear-gradient(90deg, transparent, rgba(47,79,63,0.5), transparent)"
                      : "linear-gradient(90deg, transparent, rgba(184,115,79,0.4), transparent)",
                }}
              />
              <div className="flex items-center justify-between">
                <span className="animate-pulse-glove flex size-10 items-center justify-center rounded-full border border-bronze/25 text-sm font-semibold text-bronze">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span className="rounded-full px-3 py-1 text-[0.65rem] font-semibold tracking-wide uppercase"
                  style={{ color: i === 2 ? "var(--color-emerald)" : "var(--color-terracotta)" }}
                >
                  {i === 0 ? "диалог" : i === 1 ? "прогноз" : "решение"}
                </span>
              </div>
              <h3 className="mt-4 font-display text-xl font-medium">{s.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink/65">{s.text}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}