import { BodyMaps } from "@/components/BodyMaps";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { HeroSection } from "@/components/three/HeroSection";
import { Philosophy } from "@/components/Philosophy";
import { PostpartumPreview } from "@/components/PostpartumPreview";
import { AboutSurgeon } from "@/components/AboutSurgeon";
import { HowItWorks } from "@/components/HowItWorks";
import { ContactForm } from "@/components/ContactForm";
import { FAQ } from "@/components/FAQ";
import { MarqueeStrip } from "@/components/MarqueeStrip";
import { Reveal } from "@/components/Reveal";

export default function Home() {
  return (
    <>
      <Header />
      <main className="flex-1">
        <HeroSection />
        <MarqueeStrip />
        <Philosophy />
        <BodyMaps />
        <PostpartumPreview />
        <AboutSurgeon />
        <HowItWorks />
        <FAQ />

        <section id="forma" className="aurora bg-white">
          <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
            <div className="grid gap-10 lg:grid-cols-[1.05fr_1.4fr]">
              <Reveal>
                <p className="eyebrow text-bronze">Начать разговор</p>
                <h2 className="mt-4 font-display text-3xl font-medium leading-tight sm:text-5xl">
                  Первая консультация
                  <br />
                  <span className="text-gold italic">— это знакомство</span>
                </h2>
                <p className="mt-4 max-w-md text-sm leading-relaxed text-ink/60">
                  Без обязательств, без давления. Оставьте контакты, и мы свяжемся с вами,
                  чтобы выбрать удобное время для беседы.
                </p>
                <p className="mt-6 text-xs text-ink/40">
                  Я лично просматриваю каждый запрос и отвечаю в течение рабочего дня. Если
                  случай требует срочности — позвоните напрямую.
                </p>
              </Reveal>
              <Reveal delay={0.1} className="rounded-[24px] bg-marble p-6 sm:p-10">
                <ContactForm />
              </Reveal>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}