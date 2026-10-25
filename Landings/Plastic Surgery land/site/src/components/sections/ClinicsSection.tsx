import { Reveal } from "@/components/Reveal";
import { Button } from "@/components/ui/Button";
import { clinics, site } from "@/lib/site";

export function ClinicsSection() {
  return (
    <section
      id="kliniki"
      className="relative overflow-hidden bg-ink py-14 text-white sm:py-20"
    >
      <div className="absolute inset-0 aurora-dark opacity-70" aria-hidden="true" />

      <div className="relative mx-auto max-w-7xl px-5 sm:px-8">
        <Reveal className="max-w-3xl">
          <p className="eyebrow text-sky">Клиники</p>
          <h2 className="mt-5 font-display text-4xl font-medium leading-tight sm:text-5xl">
            Четыре адреса, одна методика
          </h2>
          <p className="mt-6 text-lg leading-relaxed text-white/65">
            {site.legalName} работает на базе партнёрских клиник. Хирург, протокол
            и оснащение — одни и те же; отличаются адрес, палаты и уровень сервиса.
            На консультации сразу фиксируем клинику под дату операции.
          </p>
        </Reveal>

        <div className="mt-10 grid gap-5 sm:grid-cols-2">
          {clinics.map((c, i) => (
            <Reveal key={c.id} delay={i * 0.07} className="h-full">
              <article className="lift flex h-full flex-col rounded-3xl border border-white/10 bg-white/[0.04] p-8 backdrop-blur-sm">
                <div className="flex items-start justify-between gap-4">
                  <span className="font-display text-5xl font-semibold text-white/15">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <span className="rounded-full bg-sky/12 px-3 py-1 text-[0.62rem] font-semibold uppercase tracking-[0.16em] text-sky">
                    {c.metro}
                  </span>
                </div>
                <h3 className="mt-6 font-display text-2xl font-semibold">
                  {c.name}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-white/70">
                  {c.address}
                </p>
                <p className="mt-4 flex-1 text-sm leading-relaxed text-white/55">
                  {c.note}
                </p>
                <div className="mt-6 flex items-center gap-3 border-t border-white/10 pt-5 text-sm">
                  <span className="inline-block size-2 rounded-full bg-sky" />
                  <span className="text-white/70">
                    Операционные — ежедневно, 08:00–21:00
                  </span>
                </div>
              </article>
            </Reveal>
          ))}
        </div>

        <Reveal className="mt-10">
          <div className="flex flex-col items-start gap-5 rounded-3xl border border-white/10 bg-white/[0.03] p-8 sm:flex-row sm:items-center sm:justify-between">
            <p className="max-w-xl text-sm leading-relaxed text-white/60">
              Приезжаете из другого города? Организую проживание и трансфер:
              консультация, анализы, операция и контрольный осмотр обычно
              укладываются в 4–5 дней.
            </p>
            <Button href={site.phoneHref} variant="light">
              Подобрать клинику
            </Button>
          </div>
        </Reveal>
      </div>
    </section>
  );
}