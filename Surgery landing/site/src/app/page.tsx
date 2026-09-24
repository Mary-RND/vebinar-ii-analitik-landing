import { BodyMaps } from "@/components/BodyMaps";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { HeroSection } from "@/components/three/HeroSection";
import { Philosophy } from "@/components/Philosophy";
import { PostpartumPreview } from "@/components/PostpartumPreview";
import { AboutSurgeon } from "@/components/AboutSurgeon";
import { HowItWorks } from "@/components/HowItWorks";
import { ContactForm } from "@/components/ContactForm";
import { Reveal } from "@/components/Reveal";

export default function Home() {
  return (
    <>
      <Header />
      <main className="flex-1">
        <HeroSection />
        <Philosophy />
        <BodyMaps />
        <PostpartumPreview />
        <AboutSurgeon />
        <HowItWorks />

        <section id="forma" className="bg-white">
          <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
            <div className="grid gap-10 lg:grid-cols-[1.05fr_1.4fr]">
              <Reveal>
                <p className="eyebrow text-bronze">Начать разговор</p>
                <h2 className="mt-4 font-display text-3xl font-medium leading-tight sm:text-5xl">
                  Первая консультация
                  <br />
                  <span className="italic text-ink/60">— это знакомство</span>
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

        <section className="bg-sand/30">
          <div className="mx-auto max-w-7xl px-5 py-12 sm:px-8">
            <Reveal className="rounded-2xl bg-white p-8 ring-1 ring-ink/5 sm:p-10">
              <h3 className="font-display text-xl font-medium">Ответы на важные вопросы</h3>
              <p className="mt-2 text-sm text-ink/55">Не нашли ответ? Задайте его напрямую через форму выше.</p>
              <div className="mt-6 grid gap-4 text-sm leading-relaxed text-ink/70 sm:grid-cols-2">
                <p>Как проходит реабилитация после маммопластики?</p>
                <p>Можно ли совместить несколько зон в одну операцию?</p>
                <p>Чем мужская пластика отличается от женской?</p>
                <p>Когда можно планировать послеродовое восстановление?</p>
              </div>
            </Reveal>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}