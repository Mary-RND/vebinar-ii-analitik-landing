"use client";

import { useState } from "react";
import { BodyMap } from "@/components/three/BodyMap";
import { Button } from "@/components/ui/Button";
import { Reveal } from "@/components/Reveal";
import { bodyZones, operations, type BodyZone } from "@/lib/site";

const groups = [
  { id: "all", label: "Все" },
  { id: "face", label: "Лицо" },
  { id: "nose-ear", label: "Нос и уши" },
  { id: "breast", label: "Грудь" },
  { id: "body", label: "Тело" },
  { id: "other", label: "Другое" },
] as const;

export function DirectionsSection() {
  const [group, setGroup] = useState<(typeof groups)[number]["id"]>("all");
  const [zone, setZone] = useState<BodyZone>(bodyZones[0]);

  const visible = operations.filter(
    (o) => group === "all" || o.group === group
  );

  return (
    <section
      id="napravleniya"
      className="relative overflow-hidden bg-paper py-14 sm:py-20"
    >
      <div className="absolute inset-0 aurora opacity-60" aria-hidden="true" />

      <div className="relative mx-auto max-w-7xl px-5 sm:px-8">
        <Reveal className="max-w-3xl">
          <p className="eyebrow text-indigo">Направления</p>
          <h2 className="mt-5 font-display text-4xl font-medium leading-tight sm:text-5xl">
            Девять операций и схема, где какая зона
          </h2>
          <p className="mt-6 text-lg leading-relaxed text-slate">
            Практика хирурга закрывает лицо, грудь и контур тела. Справа —
            список с ценами, слева — схема: нажмите на зону, чтобы отфильтровать
            операции.
          </p>
        </Reveal>

        <div className="mt-10 grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:gap-14">
          <Reveal>
            <div className="lg:sticky lg:top-28">
              <BodyMap active={zone.id} onSelect={setZone} />

              <div className="mt-8 rounded-2xl border border-ink/10 bg-fog p-6">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo">
                  Выбрана зона
                </p>
                <p className="mt-3 font-display text-2xl font-semibold">
                  {zone.label}
                </p>
                <p className="mt-1 text-sm text-slate">{zone.hint}</p>
              </div>
            </div>
          </Reveal>

          <div>
            <Reveal>
              <div className="no-scrollbar -mx-5 flex gap-2 overflow-x-auto px-5 pb-2 sm:mx-0 sm:px-0">
                {groups.map((g) => (
                  <button
                    key={g.id}
                    onClick={() => setGroup(g.id)}
                    className={
                      "shrink-0 rounded-full border px-5 py-2 text-sm font-semibold transition-all " +
                      (group === g.id
                        ? "border-indigo bg-indigo text-white"
                        : "border-ink/12 bg-fog text-ink/70 hover:border-indigo hover:text-indigo")
                    }
                  >
                    {g.label}
                  </button>
                ))}
              </div>
            </Reveal>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              {visible.map((op, i) => (
                <Reveal key={op.id} delay={Math.min(i, 4) * 0.06} className="h-full">
                  <article
                    className={
                      "lift flex h-full flex-col rounded-3xl border p-6 transition-colors " +
                      (zone.ops.includes(op.id)
                        ? "border-indigo/40 bg-fog"
                        : "border-ink/10 bg-paper")
                    }
                  >
                    <div className="flex items-start justify-between gap-4">
                      <h3 className="font-display text-xl font-semibold leading-snug">
                        {op.name}
                      </h3>
                      <span className="shrink-0 rounded-full bg-mist px-3 py-1 text-xs font-semibold text-ink">
                        {op.price}
                      </span>
                    </div>
                    <p className="mt-3 text-sm leading-relaxed text-slate">
                      {op.summary}
                    </p>
                    <div className="mt-5 flex flex-wrap items-center gap-4 border-t border-ink/8 pt-4 text-xs text-slate">
                      <span>{op.duration}</span>
                      <span className="text-ink/20">·</span>
                      <span>{op.priceNote}</span>
                    </div>
                  </article>
                </Reveal>
              ))}
            </div>

            <Reveal className="mt-8">
              <div className="flex flex-col items-start gap-4 rounded-3xl bg-ink p-8 text-white sm:flex-row sm:items-center sm:justify-between">
                <p className="max-w-md text-sm leading-relaxed text-white/70">
                  Не нашли свою задачу в списке? Опишите её — скажу прямо, берусь
                  за неё или нет, и к кому обратиться.
                </p>
                <Button href="#ceny" variant="light">
                  Цены и что входит
                </Button>
              </div>
            </Reveal>
          </div>
        </div>
      </div>
    </section>
  );
}