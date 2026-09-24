"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { site } from "@/lib/site";

const nav = [
  { label: "Направления", href: "/#napravleniya" },
  { label: "Послеродовое восстановление", href: "/poslerodovoe-vosstanovlenie" },
  { label: "О хирурге и подходе", href: "/#filosofiya" },
  { label: "Контакты", href: "/#kontakty" },
];

export function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
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
      <header
        className={cn(
          "fixed inset-x-0 top-0 z-50 transition-all duration-500",
          scrolled
            ? "border-b border-ink/10 bg-marble/85 backdrop-blur-md"
            : "bg-transparent"
        )}
      >
        <div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-5 sm:px-8">
          <Link
            href="/"
            className={cn(
              "flex items-center gap-3 transition-colors duration-500",
              dark ? "text-ivory" : "text-ink"
            )}
            aria-label={site.brandName}
          >
            <span className="flex size-9 items-center justify-center rounded-full border border-current font-display text-xl font-medium leading-none">
              П
            </span>
            <span className="flex flex-col leading-tight">
              <span className="font-display text-lg font-semibold tracking-wide">
                Пластический хирург
              </span>
              <span
                className={cn(
                  "text-[0.65rem] uppercase tracking-[0.22em] transition-colors duration-500",
                  dark ? "text-ivory/60" : "text-bronze"
                )}
              >
                проводник
              </span>
            </span>
          </Link>

          <nav
            className={cn(
              "hidden items-center gap-8 lg:flex transition-colors duration-500",
              dark ? "text-ivory/85" : "text-ink/80"
            )}
          >
            {nav.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="text-sm font-medium transition-colors hover:text-terracotta"
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="hidden items-center gap-4 lg:flex">
            <Button href="/#forma" variant="ghost" tone={dark ? "dark" : "light"} className="px-6 py-2.5">
              Задать вопрос
            </Button>
          </div>

          <button
            onClick={() => setOpen(!open)}
            className={cn(
              "flex size-10 flex-col items-center justify-center gap-1.5 lg:hidden transition-colors",
              dark ? "text-ivory" : "text-ink"
            )}
            aria-label="Меню"
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
          "fixed inset-0 z-40 flex flex-col bg-graphite text-ivory transition-opacity duration-400 lg:hidden",
          open ? "opacity-100" : "pointer-events-none opacity-0"
        )}
      >
        <nav className="flex flex-1 flex-col justify-center gap-6 px-8">
          {nav.map((item, i) => (
            <Link
              key={item.label}
              href={item.href}
              onClick={() => setOpen(false)}
              className="border-b border-ivory/10 pb-4 font-display text-3xl font-medium transition-colors hover:text-terracotta"
              style={{ transitionDelay: `${i * 40}ms` }}
            >
              {item.label}
            </Link>
          ))}
          <Button
            href="/#forma"
            variant="ghost"
            tone="dark"
            className="mt-6 self-start"
            onClick={() => setOpen(false)}
          >
            Задать вопрос
          </Button>
        </nav>
        <p className="px-8 pb-10 text-sm text-ivory/50">{site.workHours}</p>
      </div>
    </>
  );
}