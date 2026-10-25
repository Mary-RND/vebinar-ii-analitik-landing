import type { Metadata } from "next";
import { Playfair_Display, Manrope } from "next/font/google";
import { ScrollProgress } from "@/components/ScrollProgress";
import "./globals.css";

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["cyrillic", "latin"],
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
});

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["cyrillic", "latin"],
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Пластический хирург в Москве — ООО «Медбизнес»",
  description:
    "Пластический хирург работает на базе четырёх клиник Москвы. Одна команда: хирург, анестезиолог, ассистент, операционная сестра и координатор. Лицо, грудь, тело. Ориентировочные цены и разбор случая из архива.",
  metadataBase: new URL("https://example.ru"),
  openGraph: {
    title: "Пластический хирург — ООО «Медбизнес»",
    description:
      "Один хирург — одна бригада — четыре клиники. Пластика лица, груди и тела в Москве.",
    locale: "ru_RU",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="ru"
      data-scroll-behavior="smooth"
      className={`${playfair.variable} ${manrope.variable} h-full antialiased scroll-smooth`}
    >
      <body className="flex min-h-full flex-col bg-fog font-sans text-ink">
        <ScrollProgress />
        {children}
      </body>
    </html>
  );
}