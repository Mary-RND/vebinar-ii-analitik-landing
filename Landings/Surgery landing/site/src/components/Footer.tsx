import Link from "next/link";
import { site } from "@/lib/site";

const footerLinks = [
  { label: "Направления", href: "/#napravleniya" },
  { label: "Послеродовое восстановление", href: "/poslerodovoe-vosstanovlenie" },
  { label: "Мужская пластика", href: "/muzhskaya-plastika" },
  { label: "О хирурге и подходе", href: "/#filosofiya" },
  { label: "Первая встреча", href: "/#pervaya-vstrecha" },
  { label: "Контакты", href: "/#kontakty" },
];

const legal = [
  { label: "Политика конфиденциальности", href: "/policy" },
  { label: "Согласие на обработку данных", href: "/policy" },
];

export function Footer() {
  return (
    <footer id="kontakty" className="bg-graphite text-ivory">
      <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 sm:py-20">
        <div className="grid gap-12 md:grid-cols-[1.3fr_1fr_1fr]">
          <div className="max-w-sm">
            <div className="flex items-center gap-3">
              <span className="flex size-10 items-center justify-center rounded-full border border-current font-display text-2xl font-medium leading-none">
                П
              </span>
              <div className="leading-tight">
                <p className="font-display text-xl font-semibold tracking-wide">
                  Пластический хирург
                </p>
                <p className="text-[0.65rem] uppercase tracking-[0.22em] text-bronze">
                  проводник
                </p>
              </div>
            </div>
            <p className="mt-6 font-display text-2xl italic text-ivory/85">
              «Проводник в разговоре с вашим телом»
            </p>
          </div>

          <div>
            <p className="eyebrow text-bronze">Сайт</p>
            <ul className="mt-5 space-y-3">
              {footerLinks.map((l) => (
                <li key={l.label}>
                  <Link
                    href={l.href}
                    className="text-sm text-ivory/75 transition-colors hover:text-terracotta"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="eyebrow text-bronze">Контакты</p>
            <ul className="mt-5 space-y-3 text-sm">
              <li>{site.address}</li>
              <li>
                <a
                  href={site.phoneHref}
                  className="transition-colors hover:text-terracotta"
                >
                  {site.phone}
                </a>
              </li>
              <li>
                <a
                  href={`https://t.me/${site.telegram.replace("@", "")}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="transition-colors hover:text-terracotta"
                >
                  Telegram: {site.telegram}
                </a>
              </li>
              <li>
                <a
                  href={`https://wa.me/${site.whatsapp.replace(/[^\d]/g, "")}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="transition-colors hover:text-terracotta"
                >
                  WhatsApp: {site.whatsapp}
                </a>
              </li>
            </ul>
            <p className="mt-5 text-xs text-ivory/50">{site.workHours}</p>
          </div>
        </div>

        <div className="mt-14 flex flex-col gap-4 border-t border-ivory/10 pt-8 text-xs text-ivory/45 sm:flex-row sm:items-center sm:justify-between">
          <p>© {new Date().getFullYear()} {site.brandName}. Все права защищены.</p>
          <div className="flex gap-6">
            {legal.map((l) => (
              <Link key={l.label} href={l.href} className="transition-colors hover:text-ivory/80">
                {l.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}