import { Reveal } from "@/components/Reveal";
import { Button } from "@/components/ui/Button";
import { site, surgeon } from "@/lib/site";

export function CtaSection() {
  return (
    <section
      id="cta"
      className="relative overflow-hidden bg-paper py-14 sm:py-20"
    >
      <div className="absolute inset-0 aurora opacity-80" aria-hidden="true" />

      <div className="relative mx-auto max-w-5xl px-5 text-center sm:px-8">
        <Reveal>
          <p className="eyebrow text-indigo">Первый шаг</p>
          <h2 className="mt-6 font-display text-4xl font-medium leading-tight sm:text-5xl lg:text-6xl">
            Напишите, что хотите изменить.
            <br />
            <span className="italic text-indigo">Отберу 5–7 случаев из архива.</span>
          </h2>
          <p className="mx-auto mt-7 max-w-2xl text-lg leading-relaxed text-slate">
            Примеры с похожим исходным строением и тем же объёмом вмешательства.
            Без записи, без обязательств и без предоплаты.
          </p>
        </Reveal>

        <Reveal delay={0.1}>
          <div className="mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button href={`https://t.me/${site.telegram.replace("@", "")}`} variant="primary" className="w-full sm:w-auto">
              Написать в Telegram
            </Button>
            <Button href={site.phoneHref} variant="outline" className="w-full sm:w-auto">
              {site.phone}
            </Button>
          </div>
        </Reveal>

        <Reveal delay={0.16}>
          <div className="mx-auto mt-10 grid max-w-3xl gap-px overflow-hidden rounded-3xl bg-ink/10 sm:grid-cols-3">
            {[
              { k: "Ответ", v: "в тот же день" },
              { k: "Предоплата", v: "не требуется" },
              { k: "Консультация", v: "40–60 минут" },
            ].map((x) => (
              <div key={x.k} className="bg-paper px-6 py-7">
                <p className="font-display text-2xl font-semibold">{x.v}</p>
                <p className="mt-2 text-xs uppercase tracking-[0.16em] text-slate">
                  {x.k}
                </p>
              </div>
            ))}
          </div>
        </Reveal>

        <Reveal delay={0.2}>
          <p className="mt-12 text-sm text-slate">
            {surgeon.name}, {surgeon.specialization} · {site.city},{" "}
            {site.workHours}
          </p>
        </Reveal>
      </div>
    </section>
  );
}