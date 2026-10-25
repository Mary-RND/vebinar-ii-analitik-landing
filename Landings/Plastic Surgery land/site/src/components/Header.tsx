"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { site } from "@/lib/site";

const nav = [
  { label: "О хирурге", href: "/#o-hirurge" },
  { label: "Бригада", href: "/#brigada" },
  { label: "Направления", href: "/#napravleniya" },
  { label: "Цены", href: "/#ceny" },
  { label: "Клиники", href: "/#kliniki" },
  { label: "Вопросы", href: "/#voprosy" },
];

export function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 32);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  const dark = !scrolled && !open;

  return (
    <>
      <a
        href="#napravleniya"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[80] focus:rounded-full focus:bg-indigo focus:px-5 focus:py-2.5 focus:text-sm focus:text-white"
      >
        Перейти к содержанию
      </a>

      <header
        className={cn(
          "fixed inset-x-0 top-0 z-50 transition-all duration-500",
          scrolled
            ? "border-b border-ink/8 bg-fog/85 backdrop-blur-xl"
            : "bg-transparent"
        )}
      >
        <div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-5 sm:px-8">
          <Link
            href="/"
            className={cn(
              "flex items-center gap-3 transition-colors duration-500",
              dark ? "text-white" : "text-ink"
            )}
            aria-label={site.legalName}
          >
            <span className="flex size-9 items-center justify-center rounded-full border border-current font-display text-lg font-semibold leading-none">
              М
            </span>
            <span className="flex flex-col leading-tight">
              <span className="font-display text-lg font-semibold tracking-wide">
                Пластический хирург
              </span>
              <span
                className={cn(
                  "text-[0.62rem] uppercase tracking-[0.24em] transition-colors duration-500",
                  dark ? "text-sky/80" : "text-indigo"
                )}
              >
                Медбизнес
              </span>
            </span>
          </Link>

          <nav
            className={cn(
              "hidden items-center gap-7 transition-colors duration-500 lg:flex",
              dark ? "text-white/80" : "text-ink/75"
            )}
          >
            {nav.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  "text-sm font-medium transition-colors",
                  dark ? "hover:text-sky" : "hover:text-indigo"
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="hidden lg:block">
            <a
              href={site.phoneHref}
              className={cn(
                "text-sm font-semibold transition-colors",
                dark ? "text-white hover:text-sky" : "text-ink hover:text-indigo"
              )}
            >
              {site.phone}
            </a>
          </div>

          <button
            onClick={() => setOpen(!open)}
            className={cn(
              "flex size-10 flex-col items-center justify-center gap-1.5 lg:hidden transition-colors",
              dark ? "text-white" : "text-ink"
            )}
            aria-label="Меню"
            aria-expanded={open}
          >
            <span
              className={cn(
                "h-px w-6 bg-current transition-transform duration-300",
                open && "translate-y-[7px] rotate-45"
              )}
            />
            <span
              className={cn(
                "h-px w-6 bg-current transition-opacity duration-300",
                open && "opacity-0"
              )}
            />
            <span
              className={cn(
                "h-px w-6 bg-current transition-transform duration-300",
                open && "-translate-y-[7px] -rotate-45"
              )}
            />
          </button>
        </div>
      </header>

      <div
        className={cn(
          "fixed inset-0 z-40 flex flex-col overflow-y-auto bg-ink text-white transition-opacity duration-400 lg:hidden",
          open ? "opacity-100" : "pointer-events-none opacity-0"
        )}
      >
        <nav className="flex flex-1 flex-col justify-center gap-5 px-8 pt-24">
          {nav.map((item, i) => (
            <Link
              key={item.label}
              href={item.href}
              onClick={() => setOpen(false)}
              className="border-b border-white/10 pb-4 font-display text-3xl font-medium transition-colors hover:text-sky"
              style={{ transitionDelay: `${i * 40}ms` }}
            >
              {item.label}
            </Link>
          ))}
          <a
            href={site.phoneHref}
            onClick={() => setOpen(false)}
            className="mt-8 self-start text-xl font-semibold text-sky"
          >
            {site.phone}
          </a>
        </nav>
        <p className="px-8 pb-10 text-sm text-white/50">{site.workHours}</p>
      </div>
    </>
  );
}