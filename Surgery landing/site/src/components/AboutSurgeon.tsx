import Image from "next/image";
import { Reveal } from "@/components/Reveal";
import { EcgDivider, PlusMark } from "@/components/Medic";

const focus = [
  "Маммопластика",
  "Абдоминопластика",
  "Блефаропластика",
  "Мужская контурная пластика",
];

export function AboutSurgeon() {
  return (
    <section className="relative bg-white">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(40% 45% at 94% 8%, rgba(139,111,71,0.09), transparent 70%), radial-gradient(38% 40% at 4% 90%, rgba(47,79,63,0.07), transparent 70%)",
        }}
      />
      <div className="relative mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
        <div className="grid gap-10 lg:grid-cols-[1.1fr_1.5fr] lg:items-center">
          <Reveal>
            <div className="relative overflow-hidden rounded-[24px] bg-sand">
              <Image
                src="https://images.pexels.com/photos/6303569/pexels-photo-6303569.jpeg?auto=compress&cs=tinysrgb&w=800"
                alt="Пластический хирург"
                width={640}
                height={800}
                className="aspect-[4/5] w-full object-cover"
                unoptimized
              />
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-ink/60 to-transparent p-5">
                <p className="font-display text-lg italic text-ivory">
                  Имя Фамилия, пластический хирург
                </p>
              </div>
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
              <span className="text-gold italic">слышит</span>
            </h2>
            <EcgDivider className="mt-5 text-terracotta/60" />
            <div className="mt-6 space-y-4 text-[1.02rem] leading-relaxed text-ink/75">
              <p>
                За Х лет практики я понял одну вещь: хорошие результаты начинаются задолго
                до операционной. Они начинаются с первого разговора — когда пациент
                формулирует, чего хочет, а я честно говорю, что из этого возможно, а что
                нет.
              </p>
              <p>
                Я работаю с лицом и телом, с женщинами и мужчинами.
              </p>
              <p className="italic text-ink/55">
                Мои пациенты возвращаются — и приводят тех, кого любят. Для меня это
                важнее любых рейтингов.
              </p>
            </div>
            <div className="mt-7 flex flex-wrap gap-2">
              {focus.map((f) => (
                <span
                  key={f}
                  className="flex items-center gap-2 rounded-full bg-marble px-4 py-2 text-xs font-medium text-ink/65 ring-1 ring-ink/5"
                >
                  <PlusMark className="size-4 text-bronze" />
                  {f}
                </span>
              ))}
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}