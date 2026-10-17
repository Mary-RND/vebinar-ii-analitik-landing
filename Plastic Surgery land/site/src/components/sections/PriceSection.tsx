import { Reveal } from "@/components/Reveal";
import { Button } from "@/components/ui/Button";
import { operations, priceExtras, site } from "@/lib/site";

export function PriceSection() {
  const cheapest = [...operations].sort((a, b) => {
    const pa = Number(a.price.replace(/\D/g, "").slice(0, 2));
    const pb = Number(b.price.replace(/\D/g, "").slice(0, 2));
    return pa - pb;
  });

  return (
    <section
      id="ceny"
      className="relative overflow-hidden bg-fog py-14 sm:py-20"
    >
      <div className="mx-auto max-w-7xl px-5 sm:px-8">
        <Reveal className="max-w-3xl">
          <p className="eyebrow text-indigo">Цены</p>
          <h2 className="mt-5 font-display text-4xl font-medium leading-tight sm:text-5xl">
            Смета по вашим данным, а не вилка «от»
          </h2>
          <p className="mt-6 text-lg leading-relaxed text-slate">
            Цена операции зависит от объёма вмешательства, способа доступа и
            материалов. На консультации считаю смету по вашим данным — разница с
            «минимальной» обычно составляет 20–30%.
          </p>
        </Reveal>

        <div className="mt-10 overflow-hidden rounded-3xl bg-paper">
          <div className="hidden grid-cols-[1.6fr_0.9fr_0.9fr_1.4fr] gap-4 border-b border-ink/8 px-8 py-5 text-xs font-semibold uppercase tracking-[0.14em] text-slate sm:grid">
            <span>Операция</span>
            <span>Стоимость</span>
            <span>Длительность</span>
            <span>Ориентир по рынку</span>
          </div>

          {operations.map((op, i) => (
            <Reveal key={op.id} delay={Math.min(i, 5) * 0.04}>
              <div className="group grid gap-3 border-b border-ink/6 px-6 py-6 transition-colors last:border-0 hover:bg-fog/70 sm:grid-cols-[1.6fr_0.9fr_0.9fr_1.4fr] sm:items-center sm:gap-4 sm:px-8">
                <div>
                  <h3 className="font-display text-lg font-semibold leading-snug">
                    {op.name}
                  </h3>
                  <p className="mt-1 text-sm text-slate sm:hidden">
                    {op.price} · {op.duration}
                  </p>
                </div>
                <p className="text-base font-semibold text-indigo sm:text-[0.95rem]">
                  {op.price}
                </p>
                <p className="text-sm text-slate sm:text-[0.95rem]">
                  {op.duration}
                </p>
                <p className="text-xs leading-relaxed text-slate">
                  {op.priceNote}
                </p>
              </div>
            </Reveal>
          ))}
        </div>

        <div className="mt-8 grid gap-5 lg:grid-cols-[1fr_1fr]">
          <Reveal>
            <div className="h-full rounded-3xl border border-ink/10 bg-paper p-8">
              <h3 className="font-display text-2xl font-semibold">
                Что не входит в цену операции
              </h3>
              <ul className="mt-5 space-y-3">
                {priceExtras.map((e) => (
                  <li
                    key={e.label}
                    className="flex items-start justify-between gap-4 border-b border-ink/6 pb-3 text-sm last:border-0"
                  >
                    <span className="text-slate">{e.label}</span>
                    <span className="shrink-0 font-semibold">{e.value}</span>
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>

          <Reveal delay={0.08}>
            <div className="flex h-full flex-col justify-between rounded-3xl bg-ink p-8 text-white">
              <div>
                <h3 className="font-display text-2xl font-semibold">
                  Самая быстрая операция
                </h3>
                <p className="mt-4 text-sm leading-relaxed text-white/70">
                  {cheapest[0]?.name} — {cheapest[0]?.price},{" "}
                  {cheapest[0]?.duration}. Чаще всего делают подросткам, но
                  ограничение только в состоянии хряща.
                </p>
              </div>
              <div className="mt-8 flex flex-wrap items-center gap-4">
                <Button href={site.phoneHref} variant="light">
                  Уточнить стоимость
                </Button>
                <p className="text-xs text-white/50">
                  Предоплата не требуется
                </p>
              </div>
            </div>
          </Reveal>
        </div>

        <Reveal className="mt-8">
          <p className="rounded-2xl border border-ink/10 bg-fog p-5 text-xs leading-relaxed text-slate">
            Цены на сайте — ориентировочные и приведены как пример оформления.
            Это демонстрационный проект: все данные вымышлены. Реальная стоимость
            определяется на очной консультации и не является публичной офертой.
          </p>
        </Reveal>
      </div>
    </section>
  );
}