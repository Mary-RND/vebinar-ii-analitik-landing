import { Reveal } from "@/components/Reveal";
import { site, socials } from "@/lib/site";

const reasons = [
  {
    title: "Кейсы с фотографиями — по запросу",
    text: "Показываю случаи лично на консультации и по мессенджеру: с исходным строением, техникой и сроками восстановления. Публичное портфолио на сайте не размещаю.",
  },
  {
    title: "Примеры подбираю под вашу задачу",
    text: "Не «красивые вообще», а похожие на ваш случай: тот же объём вмешательства и близкое исходное строение. Так честнее оценивать результат.",
  },
  {
    title: "Что важно понимать про сроки",
    text: "Окончательный вид — через 3–6 месяцев. Первые недели — отёк и неравномерность; судьбу операции по фото «сразу после» решать нельзя.",
  },
];

export function CasesSection() {
  return (
    <section
      id="primery"
      className="relative overflow-hidden bg-paper py-14 sm:py-20"
    >
      <div className="absolute inset-0 aurora opacity-60" aria-hidden="true" />

      <div className="relative mx-auto max-w-7xl px-5 sm:px-8">
        <div className="grid gap-12 lg:grid-cols-[1.05fr_0.95fr] lg:gap-16">
          <div>
            <Reveal>
              <p className="eyebrow text-indigo">Примеры работ</p>
              <h2 className="mt-5 font-display text-4xl font-medium leading-tight sm:text-5xl">
                Архив вместо галереи
              </h2>
              <p className="mt-6 text-lg leading-relaxed text-slate">
                На этом сайте нет блока «до и после». Это осознанное решение:
                фотографии пациентов публикуются только с письменного согласия, а
                выбор случаев — личный разговор, а не витрина.
              </p>
            </Reveal>

            <div className="mt-10 space-y-4">
              {reasons.map((r, i) => (
                <Reveal key={r.title} delay={i * 0.07}>
                  <div className="rounded-3xl border border-ink/10 bg-fog p-6">
                    <h3 className="font-display text-xl font-semibold">
                      {r.title}
                    </h3>
                    <p className="mt-3 text-sm leading-relaxed text-slate">
                      {r.text}
                    </p>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>

          <Reveal delay={0.1}>
            <div className="rounded-3xl bg-ink p-8 text-white sm:p-10">
              <p className="eyebrow text-sky">Куда смотреть</p>
              <h3 className="mt-5 font-display text-3xl font-semibold">
                Каналы связи
              </h3>
              <p className="mt-4 text-sm leading-relaxed text-white/65">
                Примеры работ и свободные даты — в мессенджерах. Отвечаю сам,
                без операторов и скриптов.
              </p>

              <ul className="mt-8 space-y-3">
                {socials.map((s) => (
                  <li key={s.id}>
                    <a
                      href={
                        s.id === "tg"
                          ? `https://t.me/${site.telegram.replace("@", "")}`
                          : s.id === "wa"
                            ? `https://wa.me/${site.whatsapp.replace(/[^\d]/g, "")}`
                            : "#kontakty"
                      }
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-disabled={s.id === "vk" || s.id === "yt"}
                      className={
                        "group flex items-center justify-between gap-4 rounded-2xl border px-5 py-4 transition-all " +
                        (s.id === "vk" || s.id === "yt"
                          ? "cursor-not-allowed border-white/10 bg-white/[0.02] text-white/35"
                          : "border-white/12 bg-white/[0.04] hover:border-sky/60 hover:bg-white/[0.08]")
                      }
                    >
                      <span className="flex items-center gap-4">
                        <span className="flex size-9 items-center justify-center rounded-full bg-white/8 text-xs font-bold uppercase">
                          {s.label.slice(0, 2)}
                        </span>
                        <span className="text-sm font-semibold">{s.label}</span>
                      </span>
                      <span className="text-xs text-white/45">{s.handle}</span>
                    </a>
                  </li>
                ))}
              </ul>

              <p className="mt-8 border-t border-white/10 pt-6 text-xs leading-relaxed text-white/40">
                ВКонтакте и YouTube — разделы готовятся, ссылки пока
                неактивны. Демонстрационный проект: контакты вымышленные.
              </p>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}