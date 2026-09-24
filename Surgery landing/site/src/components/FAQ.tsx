"use client";

import { useState } from "react";
import { Reveal } from "@/components/Reveal";
import { EcgDivider } from "@/components/Medic";

const faq = [
  {
    q: "Как проходит реабилитация после маммопластики?",
    a: "Первые дни — покой и компрессионное бельё, к концу первой недели большинство возвращаются к обычной активности. Полный шов заживает в течение месяца, финальная форма оценивается через несколько месяцев, когда спадает отёк. Точный план зависит от техники и даётся индивидуально.",
  },
  {
    q: "Можно ли совместить несколько зон в одну операцию?",
    a: "Да, часто это даже предпочтительнее — один наркоз, одна реабилитация. Например, абдоминопластика с липосакцией или коррекция груди вместе с животом. Оптимальный объём обсуждается после осмотра и диагностики.",
  },
  {
    q: "Чем мужская пластика отличается от женской?",
    a: "Другими пропорциями, толщиной и распределением кожи и жировой ткани, другими линейками эстетики результата и расположением разрезов. По этой причине подход и техники подбираются отдельно для мужчин и женщин.",
  },
  {
    q: "Когда можно планировать послеродовое восстановление?",
    a: "Как правило, не раньше чем через 6–12 месяцев после родов и спустя несколько месяцев после завершения кормления. Срок всегда подсказывается индивидуально: важны тонус тканей, стабильный вес и планы на будущее.",
  },
  {
    q: "Сколько длится операция и нужна ли госпитализация?",
    a: "Большинство вмешательств занимает от 2 до 4 часов и проходит в стационаре с кратковременным пребыванием. Часть операций выполняется амбулаторно. Детали — после консультации и оценки состояния.",
  },
];

export function FAQ() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section className="aurora relative bg-sand/30">
      <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 sm:py-24">
        <Reveal className="mx-auto max-w-2xl text-center">
          <p className="eyebrow text-bronze">Частые вопросы</p>
          <h2 className="mt-4 font-display text-3xl font-medium sm:text-5xl">
            Ответы на важные вопросы
          </h2>
          <div className="mt-5 flex justify-center">
            <EcgDivider className="text-terracotta/60" />
          </div>
        </Reveal>

        <div className="mx-auto mt-10 max-w-3xl space-y-3">
          {faq.map((item, i) => {
            const isOpen = open === i;
            return (
              <Reveal key={item.q} delay={i * 0.05}>
                <div
                  className={`overflow-hidden rounded-2xl bg-white ring-1 transition-all duration-300 ${
                    isOpen
                      ? "shadow-[0_20px_55px_-30px_rgba(47,79,63,0.45)] ring-emerald/25"
                      : "ring-ink/5 hover:ring-ink/10"
                  }`}
                >
                  <button
                    onClick={() => setOpen(isOpen ? null : i)}
                    aria-expanded={isOpen}
                    className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left"
                  >
                    <span
                      className={`font-display text-lg font-medium transition-colors ${
                        isOpen ? "text-emerald" : "text-ink"
                      }`}
                    >
                      {item.q}
                    </span>
                    <span
                      className={`flex size-8 shrink-0 items-center justify-center rounded-full border transition-all duration-300 ${
                        isOpen
                          ? "rotate-45 border-emerald text-emerald"
                          : "border-bronze/30 text-bronze"
                      }`}
                    >
                      <svg className="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
                        <path d="M12 5v14M5 12h14" />
                      </svg>
                    </span>
                  </button>
                  <div
                    className="grid transition-[grid-template-rows] duration-300 ease-out"
                    style={{ gridTemplateRows: isOpen ? "1fr" : "0fr" }}
                  >
                    <div className="overflow-hidden">
                      <p className="px-6 pb-5 text-sm leading-relaxed text-ink/65">
                        {item.a}
                      </p>
                    </div>
                  </div>
                </div>
              </Reveal>
            );
          })}
          <p className="pt-4 text-center text-sm text-ink/50">
            Не нашли ответ? Задайте его напрямую через{" "}
            <a href="#forma" className="font-semibold text-emerald hover:underline">
              форму выше
            </a>
            .
          </p>
        </div>
      </div>
    </section>
  );
}