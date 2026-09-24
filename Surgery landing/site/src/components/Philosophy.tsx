import { Reveal } from "@/components/Reveal";

export function Philosophy() {
  return (
    <section id="filosofiya" className="bg-marble">
      <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
        <div className="grid gap-10 lg:grid-cols-[1.05fr_1.6fr] lg:items-start">
          <Reveal>
            <p className="eyebrow text-bronze">О подходе</p>
            <h2 className="mt-4 font-display text-3xl font-medium leading-tight sm:text-5xl">
              Проводник,
              <br />
              <span className="italic text-ink/60">а&nbsp;не&nbsp;исполнитель</span>
            </h2>
          </Reveal>
          <Reveal delay={0.12} className="max-w-2xl">
            <div className="space-y-5 text-[1.02rem] leading-relaxed text-ink/80">
              <p>
                Хирургия красоты часто говорит языком результатов: миллиметры, углы,
                пропорции. Это важно, но это не всё.
              </p>
              <p>
                Прежде чем взять в руки скальпель, нужно услышать, зачем человек пришёл.
                Иногда за запросом на изменение формы стоит желание вернуться к себе — той,
                какой была до родов, до болезни, до времени. Иногда — впервые себя узнать.
              </p>
              <p>
                Моя задача — не переделать. Моя задача — провести вас от вопроса
                «а&nbsp;можно ли?» к уверенному «да, именно так».
              </p>
            </div>
            <p className="mt-8 border-l-2 border-terracotta/30 pl-4 text-sm text-ink/55">
              Имя Фамилия, пластический хирург. Стаж — Х лет.
            </p>
          </Reveal>
        </div>
      </div>
    </section>
  );
}