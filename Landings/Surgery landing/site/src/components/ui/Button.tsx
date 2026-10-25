import Link from "next/link";
import { cn } from "@/lib/utils";

type ButtonProps = {
  href?: string;
  variant?: "primary" | "ghost" | "outline" | "bronze";
  tone?: "light" | "dark";
  className?: string;
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
};

export function Button({
  href,
  variant = "primary",
  tone = "light",
  className,
  children,
  onClick,
  type = "button",
  disabled,
}: ButtonProps) {
  const base =
    "group inline-flex items-center justify-center gap-2 rounded-full px-7 py-3.5 text-[0.95rem] font-semibold tracking-tight transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald disabled:pointer-events-none disabled:opacity-50";

  const variants: Record<string, string> = {
    primary:
      "bg-terracotta text-ivory shadow-[0_10px_30px_-12px_rgba(184,115,79,0.7)] hover:bg-bronze hover:shadow-[0_14px_36px_-12px_rgba(139,111,71,0.8)]",
    bronze:
      "bg-bronze text-ivory shadow-[0_10px_30px_-12px_rgba(139,111,71,0.7)] hover:bg-terracotta",
    ghost:
      "border border-current bg-transparent hover:bg-current/5",
    outline: "border border-ink/20 bg-transparent text-inherit hover:border-current",
  };

  const toneClass = tone === "dark" ? "text-ivory" : "text-ink";

  const classes = cn(base, variants[variant], toneClass, className);

  const content = (
    <>
      {children}
      <svg
        className="size-4 shrink-0 transition-transform duration-300 group-hover:translate-x-1"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M5 12h14" />
        <path d="m12 5 7 7-7 7" />
      </svg>
    </>
  );

  if (href) {
    const isExternal = href.startsWith("http");
    if (isExternal) {
      return (
        <a href={href} className={classes} target="_blank" rel="noopener noreferrer">
          {content}
        </a>
      );
    }
    return (
      <Link href={href} className={classes}>
        {content}
      </Link>
    );
  }

  return (
    <button type={type} onClick={onClick} disabled={disabled} className={classes}>
      {content}
    </button>
  );
}