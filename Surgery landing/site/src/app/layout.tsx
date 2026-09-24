import type { Metadata } from "next";
import { Cormorant_Garamond, Manrope } from "next/font/google";
import "./globals.css";

const cormorant = Cormorant_Garamond({
  variable: "--font-cormorant",
  subsets: ["cyrillic", "latin"],
  weight: ["300", "400", "500", "600", "700"],
  style: ["normal", "italic"],
});

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["cyrillic", "latin"],
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Пластический хирург — пластика лица и тела для женщин и мужчин",
  description:
    "Пластическая хирургия лица и тела для женщин и мужчин. Без спешки. Без шаблонов. С вниманием к тому, кто вы есть. Роль бренда — проводник: послеродовое восстановление, маммопластика, мужская пластика и абдоминопластика.",
  metadataBase: new URL("https://example.ru"),
  openGraph: {
    title: "Пластический хирург — проводник в разговоре с вашим телом",
    description:
      "Пластическая хирургия лица и тела для женщин и мужчин. Без спешки. Без шаблонов.",
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
      className={`${cormorant.variable} ${manrope.variable} h-full antialiased scroll-smooth`}
    >
      <body className="flex min-h-full flex-col bg-marble font-sans text-ink">
        {children}
      </body>
    </html>
  );
}