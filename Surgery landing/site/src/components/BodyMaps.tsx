"use client";

import { useState } from "react";
import { ZoneFigure, type Zone } from "./three/ZoneFigure";
import { femaleBodyZones, maleBodyZones } from "@/lib/site";

function Card({
  kind,
  title,
  subtitle,
  accent,
  hrefBase,
  zones,
  tone = "light",
}: {
  kind: "female" | "male";
  title: string;
  subtitle: string;
  accent: string;
  hrefBase: string;
  zones: Zone[];
  tone?: "light" | "dark";
}) {
  const [picked, setPicked] = useState<Zone | null>(null);

  return (
    <div
      className={
        tone === "dark"
          ? "relative overflow-hidden rounded-[28px] bg-graphite p-6 text-ivory shadow-[0_20px_60px_-30px_rgba(0,0,0,0.5)] sm:p-8"
          : "relative overflow-hidden rounded-[28px] bg-white p-6 shadow-[0_20px_60px_-30px_rgba(42,40,37,0.22)] sm:p-8"
      }
    >
      <div
        className="pointer-events-none absolute inset-0 opacity-60"
        style={{
          background:
            tone === "dark"
              ? "radial-gradient(60% 50% at 20% 8%, rgba(139,111,71,0.16), transparent 70%), radial-gradient(50% 45% at 85% 90%, rgba(47,79,63,0.18), transparent 70%)"
              : "radial-gradient(60% 50% at 85% 12%, rgba(184,115,79,0.1), transparent 70%), radial-gradient(50% 45% at 12% 92%, rgba(139,111,71,0.08), transparent 70%)",
        }}
      />
      <div className="relative">
        <div className="flex items-center gap-3">
          <span className="size-2 rounded-full" style={{ background: accent }} />
          <p className="eyebrow" style={{ color: accent }}>
            {title}
          </p>
        </div>
        <h3 className="mt-3 font-display text-2xl font-medium">
          {kind === "female" ? "Женское тело" : "Мужское тело"}
        </h3>
        <p
          className={
            tone === "dark"
              ? "mt-2 text-sm leading-relaxed text-ivory/60"
              : "mt-2 text-sm leading-relaxed text-ink/60"
          }
        >
          {subtitle}
        </p>

        <div
          className="mt-6 overflow-hidden rounded-2xl border border-ink/5 bg-marble"
          style={
            tone === "dark"
              ? { background: "rgba(237,230,216,0.05)", borderColor: "rgba(237,230,216,0.12)" }
              : undefined
          }
        >
          <ZoneFigure
            kind={kind}
            accent={accent}
            zones={zones}
            className="h-[380px] sm:h-[420px]"
            onPick={setPicked}
          />
        </div>

        <p
          className={
            tone === "dark" ? "mt-4 text-xs text-ivory/40" : "mt-4 text-xs text-ink/40"
          }
        >
          На мобильных — коснитесь зоны.
        </p>
      </div>

      {picked && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50 p-5 backdrop-blur-sm"
          onClick={() => setPicked(null)}
        >
          <div
            className="w-full max-w-md rounded-2xl bg-white p-8 text-ink shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="eyebrow text-bronze">Вы выбрали направление</p>
            <h4 className="mt-2 font-display text-2xl font-medium">
              {picked.label}
            </h4>
            <p className="mt-2 text-sm leading-relaxed text-ink/60">
              Здесь вы найдёте подробное описание метода, реабилитации и ответов
              на частые вопросы.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <a
                href={hrefBase}
                className="inline-flex items-center gap-2 rounded-full bg-terracotta px-6 py-3 text-sm font-semibold text-ivory transition hover:bg-bronze"
              >
                Перейти к описанию <span aria-hidden>→</span>
              </a>
              <button
                onClick={() => setPicked(null)}
                className="rounded-full border border-ink/15 px-6 py-3 text-sm font-semibold transition hover:bg-ink/5"
              >
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function BodyMaps() {
  return (
    <section
      id="napravleniya"
      className="aurora relative bg-sand/40"
    >
      <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
        <div className="mx-auto max-w-2xl text-center">
          <p className="eyebrow text-bronze">Направления</p>
          <h2 className="mt-4 font-display text-3xl font-medium sm:text-5xl">
            Выберите направление
          </h2>
          <p className="mt-4 text-sm text-ink/55">
            Каждая зона — это отдельная история. Нажмите на область, чтобы
            узнать, какие решения возможны именно там.
          </p>
        </div>
        <div className="mt-12 grid gap-6 lg:grid-cols-2">
          <Card
            kind="female"
            title="Женская пластика"
            subtitle="Грудь · Живот · Бёдра · Ягодицы · Руки · Лицо"
            accent="#b8734f"
            zones={femaleBodyZones}
            hrefBase="/poslerodovoe-vosstanovlenie"
          />
          <Card
            kind="male"
            title="Мужская пластика"
            subtitle="Грудь · Живот · Спина · Лицо · Шея"
            accent="#8b6f47"
            zones={maleBodyZones}
            hrefBase="/muzhskaya-plastika"
            tone="dark"
          />
        </div>
      </div>
    </section>
  );
}