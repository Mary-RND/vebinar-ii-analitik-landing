import Image from "next/image";
import { Reveal } from "@/components/Reveal";
import { site, team } from "@/lib/site";

export function TeamSection() {
  const [lead, ...rest] = team;

  return (
    <section
      id="brigada"
      className="relative overflow-hidden bg-fog py-14 sm:py-20"
    >
      <div className="mx-auto max-w-7xl px-5 sm:px-8">
        <Reveal className="max-w-3xl">
          <p className="eyebrow text-indigo">Бригада</p>
          <h2 className="mt-5 font-display text-4xl font-medium leading-tight sm:text-5xl">
            Пять человек, которые оперируют вместе каждый год
          </h2>
          <p className="mt-6 text-lg leading-relaxed text-slate">
            Это не набор имён на сайте. Анестезиолог, ассистент и операционная
            сестра работают с {site.legalName} постоянно и участвуют в каждой
            операции. Ниже — состав рабочей группы и зона ответственности
            каждого.
          </p>
        </Reveal>

        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {rest.map((person, i) => (
            <Reveal key={person.id} delay={i * 0.07} className="h-full">
              <article className="lift group flex h-full flex-col overflow-hidden rounded-3xl bg-paper">
                <div className="relative aspect-4/5 overflow-hidden bg-mist">
                  <Image
                    src={person.photo}
                    alt={`${person.name}, ${person.role}`}
                    width={1024}
                    height={1024}
                    className="h-full w-full object-cover object-top transition-transform duration-700 group-hover:scale-105"
                  />
                  <span className="absolute left-4 top-4 rounded-full bg-white/90 px-3 py-1 text-[0.62rem] font-semibold uppercase tracking-[0.16em] text-indigo backdrop-blur-sm">
                    {String(i + 2).padStart(2, "0")}
                  </span>
                </div>
                <div className="flex flex-1 flex-col p-6">
                  <h3 className="font-display text-xl font-semibold">
                    {person.name}
                  </h3>
                  <p className="mt-1 text-sm font-semibold text-indigo">
                    {person.role}
                  </p>
                  <p className="mt-3 text-sm leading-relaxed text-slate">
                    {person.note}
                  </p>
                </div>
              </article>
            </Reveal>
          ))}
        </div>

        <Reveal className="mt-6">
          <article className="lift flex flex-col gap-6 overflow-hidden rounded-3xl bg-ink p-8 text-white sm:flex-row sm:items-center sm:p-10">
            <div className="relative size-28 shrink-0 overflow-hidden rounded-2xl bg-white/10">
              <Image
                src={lead.photo}
                alt={`${lead.name}, ${lead.role}`}
                width={1024}
                height={1024}
                className="h-full w-full object-cover object-top"
              />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <span className="rounded-full bg-sky/15 px-3 py-1 text-[0.62rem] font-semibold uppercase tracking-[0.16em] text-sky">
                  01 · ведущий
                </span>
              </div>
              <h3 className="mt-4 font-display text-3xl font-semibold">
                {lead.name}
              </h3>
              <p className="mt-1 text-sm font-semibold text-sky">
                {lead.role}
              </p>
              <p className="mt-4 max-w-2xl text-sm leading-relaxed text-white/65">
                {lead.note}. Ведёт все сложные случаи блока и отвечает за
                результат целиком — от расчёта до планового осмотра.
              </p>
            </div>
          </article>
        </Reveal>
      </div>
    </section>
  );
}