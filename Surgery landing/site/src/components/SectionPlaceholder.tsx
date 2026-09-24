import { Reveal } from "@/components/Reveal";

type Props = {
  kicker?: string;
  title: string;
  note?: string;
};

export function SectionPlaceholder({ kicker, title, note }: Props) {
  return (
    <div className="mx-auto max-w-7xl px-5 py-28 sm:px-8 sm:py-36">
      <Reveal className="mx-auto max-w-2xl text-center">
        {kicker && (
          <p className="eyebrow text-bronze">{kicker}</p>
        )}
        <h2 className="mt-4 font-display text-3xl font-medium leading-tight sm:text-5xl">
          {title}
        </h2>
        {note && (
          <p className="mt-4 text-sm italic text-ink/40">{note}</p>
        )}
      </Reveal>
    </div>
  );
}