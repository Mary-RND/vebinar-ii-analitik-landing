import Image from "next/image";
import { Reveal } from "@/components/Reveal";

export function AboutSurgeon() {
  return (
    <section className="bg-white">
      <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
        <div className="grid gap-10 lg:grid-cols-[1.1fr_1.5fr] lg:items-center">
          <Reveal>
            <div className="overflow-hidden rounded-[24px] bg-sand">
              <Image
                src="https://images.pexels.com/photos/5327585/pexels-photo-5327585.jpeg?auto=compress&cs=tinysrgb&w=800"
                alt="Пластический хирург"
                width={640}
                height={800}
                className="aspect-[4/5] w-full object-cover"
                unoptimized
              />
            </div>
            <p className="mt-3 text-center text-xs text-ink/40">
              Фото — плейсхолдер (лицензионный сток, будет заменено на реальное)
            </p>
          </Reveal>
          <Reveal delay={0.1} className="max-w-xl lg:pl-6">
            <p className="eyebrow text-bronze">О хирурге</p>
            <h2 className="mt-4 font-display text-3xl font-medium leading-tight sm:text-5xl">
              Опыт, который
              <br />
              <span className="italic text-ink/60">слышит</span>
            </h2>
            <div className="mt-6 space-y-4 text-[1.02rem] leading-relaxed text-ink/75">
              <p>
                За Х лет практики я понял одну вещь: хорошие результаты начинаются задолго
                до операционной. Они начинаются с первого разговора — когда пациент
                формулирует, чего хочет, а я честно говорю, что из этого возможно, а что
                нет.
              </p>
              <p>
                Я работаю с лицом и телом, с женщинами и мужчинами. Специализируюсь на
                маммопластике, абдоминопластике, блефаропластике, мужской контурной
                пластике.
              </p>
              <p className="italic text-ink/55">
                Мои пациенты возвращаются — и приводят тех, кого любят. Для меня это
                важнее любых рейтингов.
              </p>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}