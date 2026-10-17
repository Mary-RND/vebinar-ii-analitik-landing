import Link from "next/link";
import { site, surgeon } from "@/lib/site";

const columns = [
  {
    title: "Разделы",
    links: [
      { label: "О хирурге", href: "/#o-hirurge" },
      { label: "Бригада", href: "/#brigada" },
      { label: "Направления", href: "/#napravleniya" },
      { label: "Цены", href: "/#ceny" },
    ],
  },
  {
    title: "Организация",
    links: [
      { label: "Клиники", href: "/#kliniki" },
      { label: "Как проходит", href: "/#kak-prohodit" },
      { label: "Примеры работ", href: "/#primery" },
      { label: "Вопросы", href: "/#voprosy" },
    ],
  },
];

export function Footer() {
  return (
    <footer id="kontakty" className="relative overflow-hidden bg-ink text-white">
      <div className="absolute inset-0 aurora-dark opacity-70" aria-hidden="true" />
      <div className="relative mx-auto max-w-7xl px-5 py-16 sm:px-8 sm:py-24">
        <div className="grid gap-12 lg:grid-cols-[1.4fr_1fr_1fr]">
          <div className="max-w-sm">
            <div className="flex items-center gap-3">
              <span className="flex size-10 items-center justify-center rounded-full border border-white/40 font-display text-xl font-semibold leading-none">
                М
              </span>
              <div className="leading-tight">
                <p className="font-display text-xl font-semibold">
                  Пластический хирург
                </p>
                <p className="text-[0.62rem] uppercase tracking-[0.24em] text-sky">
                  {site.legalName}
                </p>
              </div>
            </div>
            <p className="mt-6 font-display text-2xl italic text-white/85">
              {site.tagline}
            </p>
            <p className="mt-6 text-sm leading-relaxed text-white/55">
              {surgeon.name} — хирург, {surgeon.experience} лет практики,
              2 800 операций. Работает на базе четырёх клиник Москвы и
              Подмосковья.
            </p>
          </div>

          {columns.map((col) => (
            <div key={col.title}>
              <p className="eyebrow text-sky">{col.title}</p>
              <ul className="mt-5 space-y-3">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      href={l.href}
                      className="text-sm text-white/70 transition-colors hover:text-sky"
                    >
                      {l.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <div>
            <p className="eyebrow text-sky">Контакты</p>
            <ul className="mt-5 space-y-3 text-sm">
              <li>
                <a
                  href={site.phoneHref}
                  className="font-semibold transition-colors hover:text-sky"
                >
                  {site.phone}
                </a>
              </li>
              <li>
                <a
                  href={`https://t.me/${site.telegram.replace("@", "")}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-white/70 transition-colors hover:text-sky"
                >
                  Telegram: {site.telegram}
                </a>
              </li>
              <li className="text-white/60">{site.city}, четыре клиники</li>
            </ul>
            <p className="mt-5 text-xs text-white/45">{site.workHours}</p>
          </div>
        </div>

        <div className="mt-10 border-t border-white/10 pt-8">
          <p className="text-xs leading-relaxed text-white/40">
            Демонстрационный сайт. Все данные — вымышленные: имена, клиники,
            цены и статистика приведены как пример оформления и не являются
            публичной офертой или медицинской рекомендацией.
          </p>
          <p className="mt-4 text-xs leading-relaxed text-white/40">
            3D-модель в шапке: «Statue of Aphrodite with dolphin», автор
            OmarElAtabany,{" "}
            <a
              href="https://commons.wikimedia.org/wiki/File:Statue_of_Aphrodite_with_dolphin,_3D_photogrammetry_scan_(STL).stl"
              target="_blank"
              rel="noopener noreferrer"
              className="underline decoration-white/25 underline-offset-2 transition-colors hover:text-sky"
            >
              Wikimedia Commons
            </a>
            ,{" "}
            <a
              href="https://creativecommons.org/licenses/by-sa/4.0/deed.ru"
              target="_blank"
              rel="noopener noreferrer"
              className="underline decoration-white/25 underline-offset-2 transition-colors hover:text-sky"
            >
              CC BY-SA 4.0
            </a>
            ; адаптировано (срез основания, оптимизация меша).
          </p>
          <div className="mt-6 flex flex-col gap-3 text-xs text-white/45 sm:flex-row sm:items-center sm:justify-between">
            <p>
              © {new Date().getFullYear()} {site.legalName}
            </p>
            <p>Использование материалов сайта — с указанием источника</p>
          </div>
        </div>
      </div>
    </footer>
  );
}