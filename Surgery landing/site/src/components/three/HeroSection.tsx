"use client";

import { useRef, type CSSProperties } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { HeroScene, type HeroDriver } from "./HeroScene";
import { useIsMobile, useWebGL } from "@/hooks/useWebGL";
import { EcgDivider } from "@/components/Medic";

gsap.registerPlugin(ScrollTrigger, useGSAP);

const overlay = "pointer-events-none absolute inset-0 flex items-center justify-center";

function StatueFallback() {
  return (
    <div className={`${overlay} px-6`}>
      <svg
        viewBox="0 0 800 520"
        className="h-full max-h-[72vh] w-full max-w-5xl opacity-90"
        aria-hidden="true"
      >
        <defs>
          <radialGradient id="fbg-f" cx="50%" cy="42%" r="60%">
            <stop offset="0%" stopColor="#3a424c" />
            <stop offset="55%" stopColor="#252b31" />
            <stop offset="100%" stopColor="#17191d" />
          </radialGradient>
          <linearGradient id="figF" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#f6f1e7" />
            <stop offset="100%" stopColor="#cdc2ae" />
          </linearGradient>
          <linearGradient id="figM" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#3d444d" />
            <stop offset="100%" stopColor="#202529" />
          </linearGradient>
        </defs>
        <rect width="800" height="520" fill="url(#fbg-f)" rx="24" />
        <ellipse cx="266" cy="430" rx="150" ry="14" fill="#141619" opacity="0.8" />
        <ellipse cx="534" cy="430" rx="150" ry="14" fill="#141619" opacity="0.8" />
        <path
          d="M182 430 V320 c0-70 40-92 84-92 44 0 84 22 84 92 v110 z"
          fill="#2b3138"
        />
        <path
          d="M216 272 q20-18 34-6 M282 272 q-20-18-34-6 M249 214 a12 12 0 1 0-24 0 a12 12 0 1 0 24 0 M218 300 q28-12 60-4 q32-8 58 4"
          fill="none"
          stroke="#202529"
          strokeWidth="8"
          strokeLinecap="round"
        />
        <path
          d="M350 430 V320 c0-64 38-88 84-88 46 0 84 24 84 88 v110 z"
          fill="url(#figF)"
        />
        <path
          d="M380 278 q20-16 34-6 M452 278 q-20-16-34-6 M417 218 a12 12 0 1 0-24 0 a12 12 0 1 0 24 0 M384 306 q30-10 62-4 q32-6 62 4"
          fill="none"
          stroke="#d9cfbc"
          strokeWidth="8"
          strokeLinecap="round"
        />
        <rect x="154" y="410" width="148" height="26" rx="13" fill="#20252a" opacity="0.9" />
        <rect x="498" y="410" width="148" height="26" rx="13" fill="#f2ecdf" opacity="0.9" />
      </svg>
    </div>
  );
}

export function HeroSection() {
  const supported = useWebGL();
  const isMobile = useIsMobile();
  const wrapRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const branchRef = useRef<HTMLDivElement>(null);
  const hintRef = useRef<HTMLDivElement>(null);

  const driverRef = useRef<HeroDriver>({ progress: 0, pointer: { x: 0, y: 0 } });

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
          driverRef.current.progress = self.progress;
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

      tl.to(
        textRef.current,
        { opacity: 0, y: -60, ease: "none" },
        0.08
      )
        .to(
          branchRef.current,
          {
            opacity: 1,
            y: 0,
            stagger: 0.05,
            ease: "none",
          },
          0.25
        );

      gsap.to(hintRef.current, {
        opacity: 0,
        duration: 1,
        delay: 3.2,
        ease: "power2.out",
      });
    },
    { scope: wrapRef }
  );

  const onPointerMove = (e: React.PointerEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    driverRef.current.pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    driverRef.current.pointer.y = ((e.clientY - rect.top) / rect.height) * 2 - 1;
  };

  const cssFigure = {
    "--tw-shadow": "0 30px 80px -20px rgba(0,0,0,0.6)",
  } as CSSProperties;

  return (
    <section
      ref={wrapRef}
      className="relative h-[200vh] bg-graphite"
      onPointerMove={onPointerMove}
    >
      <div className="sticky top-0 h-screen overflow-hidden grain">
        {supported !== false && (
          <div className="absolute inset-0">
            <HeroScene driver={driverRef.current} />
          </div>
        )}
        {supported === false && <StatueFallback />}
        {!isMobile && supported === null && (
          <div className="absolute inset-0 bg-graphite" />
        )}

        {/* Hero text */}
        <div
          ref={textRef}
          className="pointer-events-none absolute inset-x-0 top-[13%] flex flex-col items-center px-6 text-center sm:top-[15%] sm:px-10"
        >
          <p className="eyebrow text-terracotta/90 mix-blend-screen">
            роль — проводник
          </p>
          <EcgDivider className="mt-4 text-terracotta/70" />
          <h1 className="mt-5 max-w-3xl font-display text-3xl font-medium leading-tight text-ivory sm:text-5xl md:text-[3.4rem]">
            Тело — это не проект.
            <br />
            <span className="italic text-ivory/75">
              Это разговор, который длится всю жизнь.
            </span>
          </h1>
          <p className="mt-6 max-w-xl text-base leading-relaxed text-ivory/65 sm:text-lg">
            Пластическая хирургия лица и тела для женщин и мужчин. Без спешки.
            Без шаблонов. С вниманием к тому, кто вы есть.
          </p>
          <div className="pointer-events-auto mt-10">
            <a
              href="#forma"
              className="animate-pulse-glove inline-flex items-center gap-2 rounded-full border border-ivory/50 px-7 py-3.5 text-[0.95rem] font-semibold text-ivory transition-all duration-300 hover:border-ivory hover:bg-ivory/10"
            >
              Начать разговор
              <svg
                className="size-4 transition-transform duration-300 group-hover:translate-x-1"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M5 12h14" />
                <path d="m12 5 7 7-7 7" />
              </svg>
            </a>
          </div>
        </div>

        {/* Hint */}
        <div
          ref={hintRef}
          className="absolute inset-x-0 bottom-10 flex justify-center px-6"
        >
          <div className="pointer-events-auto flex items-center gap-3 rounded-full border border-ivory/15 bg-ivory/5 px-5 py-2.5 text-sm text-ivory/70 backdrop-blur-sm">
            <span className="relative flex size-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-terracotta opacity-75" />
              <span className="relative inline-flex size-2 rounded-full bg-terracotta" />
            </span>
            Исследуйте форму. Наведите курсор на скульптуры, чтобы узнать о направлениях
          </div>
        </div>

        {/* Scroll cue */}
        <div className="pointer-events-none absolute bottom-6 left-1/2 hidden -translate-x-1/2 flex-col items-center gap-2 text-ivory/40 sm:flex">
          <span className="text-[0.65rem] uppercase tracking-[0.28em]">
            листайте — фигуры разойдутся
          </span>
          <svg className="size-4 animate-bounce" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 5v14" />
            <path d="m19 12-7 7-7-7" />
          </svg>
        </div>

        {/* Branch labels that appear on scroll-split */}
        <div
          ref={branchRef}
          className="pointer-events-none absolute inset-0 flex items-center justify-between px-8 opacity-0 sm:px-14 md:px-20"
          style={{ transform: "translateY(10px)" }}
        >
          <a
            href="/#napravleniya"
            className="pointer-events-auto group flex flex-col items-start gap-3 text-ivory"
          >
            <span className="flex size-2 rounded-full bg-terracotta" />
            <span className="font-display text-2xl font-medium sm:text-4xl">
              Женская пластика
            </span>
            <span className="text-sm text-ivory/60 transition-colors group-hover:text-ivory">
              Грудь · Живот · Бёдра · Ягодицы · Руки · Лицо
            </span>
          </a>
          <a
            href="/#napravleniya"
            className="pointer-events-auto group flex flex-col items-end gap-3 text-right text-ivory"
          >
            <span className="flex size-2 rounded-full bg-bronze" />
            <span className="font-display text-2xl font-medium sm:text-4xl">
              Мужская пластика
            </span>
            <span className="text-sm text-ivory/60 transition-colors group-hover:text-ivory">
              Грудь · Живот · Спина · Лицо · Шея
            </span>
          </a>
        </div>
      </div>
    </section>
  );
}