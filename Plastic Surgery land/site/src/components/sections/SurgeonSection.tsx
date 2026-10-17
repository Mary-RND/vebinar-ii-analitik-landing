import Image from "next/image";
import { Reveal } from "@/components/Reveal";
import { Button } from "@/components/ui/Button";
import { site, surgeon } from "@/lib/site";

const stats = [
  { value: `${surgeon.experience}`, label: "лет практики" },
  { value: `${surgeon.operations.toLocaleString("ru-RU")}`, label: "операций" },
  { value: "9", label: "лет в одной бригаде" },
  { value: "2", label: "сложных случая в месяц" },
];

export function SurgeonSection() {
  return (
    <section
      id="o-hirurge"
      className="relative overflow-hidden bg-ink py-14 text-white sm:py-20"
    >
      <div className="absolute inset-0 aurora-dark opacity-80" aria-hidden="true" />

      <div className="relative mx-auto grid max-w-7xl gap-12 px-5 sm:px-8 lg:grid-cols-[0.85fr_1.15fr] lg:gap-16">
        <Reveal className="order-2 lg:order-1">
          <div className="relative">
            <div className="overflow-hidden rounded-[2rem] bg-white/5">
              <Image
                src={surgeon.photo}
                alt={`${surgeon.name}, ${surgeon.role}`}
                width={1024}
                height={1024}
                className="h-full w-full object-cover object-top"
                priority={false}
              />
            </div>
            <div className="absolute -bottom-6 -right-4 rounded-2xl border border-white/12 bg-ink/80 px-5 py-4 backdrop-blur-md sm:right-6">
              <p className="font-display text-lg font-semibold">{surgeon.name}</p>
              <p className="text-xs text-white/55">
                {surgeon.experience} лет · {surgeon.specialization}
              </p>
            </div>
          </div>
        </Reveal>

        <div className="order-1 lg:order-2">
          <Reveal>
            <p className="eyebrow text-sky">О хирурге</p>
            <h2 className="mt-5 max-w-2xl font-display text-4xl font-medium leading-tight sm:text-5xl">
              {surgeon.name}
            </h2>
            <p className="mt-3 text-slate-200/60">{surgeon.role}</p>
          </Reveal>

          <div className="mt-8 space-y-5">
            {surgeon.bio.map((p, i) => (
              <Reveal key={i} delay={i * 0.06}>
                <p className="max-w-2xl text-[1.02rem] leading-relaxed text-white/75">
                  {p}
                </p>
              </Reveal>
            ))}
          </div>

          <Reveal className="mt-10">
            <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-2xl bg-white/10 sm:grid-cols-4">
              {stats.map((s) => (
                <div key={s.label} className="bg-ink/85 px-5 py-6 text-center">
                  <dt className="font-display text-4xl font-semibold text-sky">
                    {s.value}
                  </dt>
                  <dd className="mt-2 text-xs uppercase tracking-[0.16em] text-white/50">
                    {s.label}
                  </dd>
                </div>
              ))}
            </dl>
          </Reveal>

          <Reveal className="mt-10">
            <h3 className="eyebrow text-white/50">Принципы</h3>
            <ul className="mt-6 grid gap-4 sm:grid-cols-2">
              {surgeon.principles.map((pr) => (
                <li
                  key={pr.title}
                  className="rounded-2xl border border-white/10 bg-white/[0.04] p-5"
                >
                  <p className="font-display text-lg font-semibold">
                    {pr.title}
                  </p>
                  <p className="mt-2 text-sm leading-relaxed text-white/60">
                    {pr.text}
                  </p>
                </li>
              ))}
            </ul>
          </Reveal>

          <Reveal className="mt-10">
            <div className="flex flex-wrap items-center gap-4">
              <Button href="#ceny" variant="light">
                Посмотреть цены
              </Button>
              <a
                href={site.phoneHref}
                className="text-sm font-semibold text-white/75 underline decoration-white/30 underline-offset-4 transition-colors hover:text-sky"
              >
                {site.phone}
              </a>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}