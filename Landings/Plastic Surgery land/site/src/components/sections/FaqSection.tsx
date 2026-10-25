"use client";

import { useState } from "react";
import { Reveal } from "@/components/Reveal";
import { site, faq } from "@/lib/site";

export function FaqSection() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section
      id="voprosy"
      className="relative overflow-hidden bg-fog py-14 sm:py-20"
    >
      <div className="mx-auto grid max-w-7xl gap-12 px-5 sm:px-8 lg:grid-cols-[0.8fr_1.2fr] lg:gap-16">
        <Reveal>
          <p className="eyebrow text-indigo">Вопросы</p>
          <h2 className="mt-5 font-display text-4xl font-medium leading-tight sm:text-5xl">
            Что спрашивают чаще всего
          </h2>
          <p className="mt-6 text-lg leading-relaxed text-slate">
            Если вашего вопроса здесь нет — напишите, отвечу без шаблонных
            формулировок.
          </p>
          <a
            href={site.phoneHref}
            className="mt-8 inline-block font-display text-2xl font-semibold text-indigo underline decoration-indigo/30 underline-offset-8 transition-colors hover:text-lilac"
          >
            {site.phone}
          </a>
        </Reveal>

        <div className="space-y-3">
          {faq.map((item, i) => {
            const isOpen = open === i;
            return (
              <Reveal key={item.q} delay={Math.min(i, 4) * 0.05}>
                <div
                  className={
                    "overflow-hidden rounded-2xl border transition-colors " +
                    (isOpen
                      ? "border-indigo/35 bg-paper"
                      : "border-ink/10 bg-paper/70")
                  }
                >
                  <button
                    onClick={() => setOpen(isOpen ? null : i)}
                    aria-expanded={isOpen}
                    className="flex w-full items-center justify-between gap-6 px-6 py-5 text-left"
                  >
                    <span className="font-display text-lg font-semibold">
                      {item.q}
                    </span>
                    <span
                      className={
                        "flex size-8 shrink-0 items-center justify-center rounded-full border transition-all " +
                        (isOpen
                          ? "rotate-45 border-indigo bg-indigo text-white"
                          : "border-ink/15 text-ink/60")
                      }
                      aria-hidden="true"
                    >
                      <svg
                        viewBox="0 0 24 24"
                        className="size-4"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      >
                        <path d="M12 5v14" />
                        <path d="M5 12h14" />
                      </svg>
                    </span>
                  </button>
                  <div
                    className={
                      "grid transition-all duration-400 ease-out " +
                      (isOpen
                        ? "grid-rows-[1fr] opacity-100"
                        : "grid-rows-[0fr] opacity-0")
                    }
                  >
                    <div className="overflow-hidden">
                      <p className="px-6 pb-6 text-sm leading-relaxed text-slate">
                        {item.a}
                      </p>
                    </div>
                  </div>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}