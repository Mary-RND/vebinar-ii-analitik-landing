import { Reveal } from "@/components/Reveal";
import { Button } from "@/components/ui/Button";
import { site, steps } from "@/lib/site";

export function StepsSection() {
  return (
    <section
      id="kak-prohodit"
      className="relative overflow-hidden bg-fog py-14 sm:py-20"
    >
      <div className="mx-auto max-w-7xl px-5 sm:px-8">
        <Reveal className="max-w-3xl">
          <p className="eyebrow text-indigo">Как проходит</p>
          <h2 className="mt-5 font-display text-4xl font-medium leading-tight sm:text-5xl">
            Шесть шагов от заявки до контрольного осмотра
          </h2>
          <p className="mt-6 text-lg leading-relaxed text-slate">
            Первый шаг ничего не стоит и ни к чему не обязывает. Дальше вы
            двигаетесь в своём темпе — паузы между этапами допустимы.
          </p>
        </Reveal>

        <ol className="mt-10 space-y-px overflow-hidden rounded-3xl bg-ink/8">
          {steps.map((s, i) => (
            <Reveal key={s.n} delay={Math.min(i, 4) * 0.05}>
              <li className="group grid gap-4 bg-fog px-6 py-8 transition-colors hover:bg-paper sm:grid-cols-[auto_1fr_auto] sm:items-start sm:gap-8 sm:px-8">
                <span className="font-display text-5xl font-semibold text-mist transition-colors group-hover:text-lilac sm:text-6xl">
                  {s.n}
                </span>
                <div>
                  <h3 className="font-display text-2xl font-semibold">
                    {s.title}
                  </h3>
                  <p className="mt-3 max-w-2xl text-[0.95rem] leading-relaxed text-slate">
                    {s.text}
                  </p>
                </div>
                <span className="w-fit shrink-0 rounded-full border border-ink/12 bg-paper px-4 py-1.5 text-xs font-semibold text-ink/70">
                  {s.duration}
                </span>
              </li>
            </Reveal>
          ))}
        </ol>

        <Reveal className="mt-10">
          <div className="flex flex-col items-start gap-5 rounded-3xl bg-paper p-8 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="font-display text-2xl font-semibold">
                Первый шаг — бесплатный
              </h3>
              <p className="mt-2 max-w-xl text-sm leading-relaxed text-slate">
                Опишите задачу — покажу 5–7 случаев из архива с похожим исходным
                строением. Без записи и обязательств.
              </p>
            </div>
            <Button href="#primery" variant="primary">
              Смотреть архив
            </Button>
          </div>
        </Reveal>

        <Reveal className="mt-6">
          <p className="text-xs text-slate">
            Анализы можно сдать в любой лаборатории — направление выдаём на
            консультации. {site.workHours}
          </p>
        </Reveal>
      </div>
    </section>
  );
}