"use client";

import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { HeroScene } from "./HeroScene";
import { heroDriver } from "./driver";
import { useIsMobile, useWebGL } from "@/hooks/useWebGL";
import { site } from "@/lib/site";
import { Button } from "@/components/ui/Button";

gsap.registerPlugin(ScrollTrigger, useGSAP);

const zones = [
  { label: "Лицо", sub: "веки · нос · уши", color: "#a9dcec" },
  { label: "Грудь", sub: "объём · форма · подтяжка", color: "#f3f5fb" },
  { label: "Тело", sub: "живот · бёдра · спина", color: "#b9bdf0" },
];

function SculptureFallback() {
  return (
    <div className="pointer-events-none absolute inset-0 flex items-center justify-center px-6 lg:justify-end lg:pr-[8%]">
      <svg
        viewBox="0 0 520 640"
        className="h-full max-h-[78vh] w-full max-w-md"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="fb-a" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#b9bdf0" />
            <stop offset="100%" stopColor="#8f8ce8" />
          </linearGradient>
          <linearGradient id="fb-b" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#f3f5fb" />
            <stop offset="100%" stopColor="#d5dcf3" />
          </linearGradient>
          <linearGradient id="fb-c" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#a9dcec" />
            <stop offset="100%" stopColor="#5ec8e4" />
          </linearGradient>
        </defs>
        <g opacity="0.55" stroke="#5ec8e4" fill="none" strokeWidth="1.5">
          <ellipse cx="260" cy="250" rx="150" ry="26" />
          <ellipse cx="260" cy="380" rx="168" ry="30" />
          <ellipse cx="260" cy="500" rx="140" ry="24" />
        </g>
        <path
          d="M260 150 c34 0 52 26 52 58 0 22-8 36-18 46 26 12 42 34 42 62 0 40-32 66-76 66s-76-26-76-66c0-28 16-50 42-62-10-10-18-24-18-46 0-32 18-58 52-58z"
          fill="url(#fb-b)"
        />
        <ellipse cx="260" cy="512" rx="86" ry="30" fill="url(#fb-a)" />
        <circle cx="260" cy="132" r="52" fill="url(#fb-c)" />
      </svg>
    </div>
  );
}

export function HeroSection() {
  const supported = useWebGL();
  const isMobile = useIsMobile();
  const wrapRef = useRef<HTMLElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const hintRef = useRef<HTMLDivElement>(null);

  const driver = heroDriver;

  useGSAP(
    () => {
      const wrap = wrapRef.current;
      if (!wrap) return;

      ScrollTrigger.create({
        trigger: wrap,
        start: "top top",
        end: "bottom bottom",
        scrub: 0.7,
        onUpdate: (self) => {
          driver.progress = self.progress;
        },
      });

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: wrap,
          start: "top top",
          end: "bottom bottom",
          scrub: 0.7,
        },
      });

      // Вся левая колонка (заголовок + карточки зон) уходит вместе —
// на старте экран заполнен, пустоты нет.
      tl.to(textRef.current, { opacity: 0, y: -60, duration: 0.42, ease: "none" }, 0.1);

      gsap.to(hintRef.current, {
        opacity: 0,
        duration: 1,
        delay: 3.4,
        ease: "power2.out",
      });

      const parts = textRef.current
        ? Array.from(textRef.current.children)
        : [];
      if (parts.length) {
        gsap.from(parts, {
          opacity: 0,
          y: 26,
          duration: 1.1,
          stagger: 0.11,
          delay: 0.25,
          ease: "power3.out",
          clearProps: "opacity,transform",
        });
      }
    },
    { scope: wrapRef }
  );

  const onPointerMove = (e: React.PointerEvent<HTMLElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    driver.pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    driver.pointer.y = ((e.clientY - rect.top) / rect.height) * 2 - 1;
  };

  return (
    <section
      ref={wrapRef}
      id="hero"
      className="relative h-[160vh] bg-ink"
      onPointerMove={onPointerMove}
    >
      <div className="sticky top-0 h-screen overflow-hidden">
        <div className="absolute inset-0 bg-[#141a30]" />
        {supported !== false && (
          <div className="absolute inset-0">
            <HeroScene driver={driver} />
          </div>
        )}
        {supported === false && <SculptureFallback />}
        {!isMobile && supported === null && (
          <div className="absolute inset-0 aurora-dark opacity-60" />
        )}

        <div
          aria-hidden="true"
          className="absolute inset-x-0 top-0 h-[60%] bg-gradient-to-b from-ink/95 via-ink/70 to-transparent lg:hidden"
        />

        <div className="pointer-events-none absolute inset-0 flex items-center">
          <div className="mx-auto w-full max-w-7xl px-5 sm:px-8 lg:px-14 xl:px-20">
            <div
              ref={textRef}
              className="mx-auto max-w-2xl text-center lg:mx-0 lg:max-w-[54%] lg:text-left"
            >
              <p className="eyebrow text-sky">
                {site.legalName} · {site.city}
              </p>
              <h1 className="mt-4 font-display text-4xl font-medium leading-[1.08] text-white sm:text-5xl lg:text-[3.4rem] xl:text-[3.9rem]">
                {site.tagline.split(",").slice(0, 2).join(",")}
                <br />
                <span className="italic text-white/70">
                  {site.tagline.split(",").slice(2).join(",").trim()}
                </span>
              </h1>
              <p className="mt-5 max-w-xl text-base leading-relaxed text-white/65 sm:text-lg lg:max-w-lg">
                {site.city}. Лицо, грудь, контур тела. Одной командой хирурга,
                анестезиолога, ассистента, операционной сестры и координатора.
              </p>
              <div className="pointer-events-auto mt-8 flex flex-col items-center gap-3 sm:flex-row lg:justify-start">
                <Button href="#napravleniya" variant="light">
                  Смотреть направления
                </Button>
                <a
                  href={site.phoneHref}
                  className="inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-7 py-3.5 text-[0.95rem] font-semibold text-white backdrop-blur-md transition-colors hover:border-white/70 hover:bg-white/20"
                >
                  {site.phone}
                </a>
              </div>

              <div className="mt-9 hidden grid-cols-3 gap-3 sm:grid">
                {zones.map((z) => (
                  <div
                    key={z.label}
                    className="pointer-events-auto rounded-2xl border border-white/15 bg-ink/75 px-4 py-4 text-left text-white backdrop-blur-md transition-colors hover:border-white/40 hover:bg-ink/90"
                  >
                    <div className="flex items-center gap-2">
                      <span
                        className="size-2 shrink-0 rounded-full"
                        style={{ background: z.color }}
                      />
                      <span className="font-display text-xl font-medium lg:text-2xl">
                        {z.label}
                      </span>
                    </div>
                    <p className="mt-1 text-xs leading-snug text-white/55">
                      {z.sub}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div
          ref={hintRef}
          className="absolute inset-x-0 bottom-6 flex justify-center px-5 sm:justify-end sm:px-8"
        >
          <div className="flex items-center gap-3 rounded-full border border-white/12 bg-ink/60 px-5 py-2.5 text-sm text-white/70 backdrop-blur-md">
            <span className="relative flex size-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-sky opacity-75" />
              <span className="relative inline-flex size-2 rounded-full bg-sky" />
            </span>
            <span className="hidden sm:inline">01 / 11 ·</span>
            <span>Листайте — форма провернётся</span>
          </div>
        </div>
      </div>
    </section>
  );
}