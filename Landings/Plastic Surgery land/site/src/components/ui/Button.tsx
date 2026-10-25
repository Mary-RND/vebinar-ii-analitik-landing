import Link from "next/link";
import { cn } from "@/lib/utils";

type ButtonProps = {
  href?: string;
  variant?: "primary" | "ghost" | "outline" | "light";
  className?: string;
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
};

export function Button({
  href,
  variant = "primary",
  className,
  children,
  onClick,
  type = "button",
  disabled,
}: ButtonProps) {
  const base =
    "group inline-flex items-center justify-center gap-2 rounded-full px-7 py-3.5 text-[0.95rem] font-semibold tracking-tight transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky disabled:pointer-events-none disabled:opacity-50";

  const variants: Record<string, string> = {
    primary:
      "btn-shine bg-indigo text-white shadow-[0_14px_40px_-16px_rgba(67,72,200,0.85)] hover:bg-lilac hover:shadow-[0_18px_46px_-16px_rgba(143,140,232,0.9)]",
    light:
      "btn-shine bg-white text-ink shadow-[0_14px_40px_-16px_rgba(20,26,48,0.5)] hover:bg-mist",
    ghost: "border border-current bg-transparent hover:bg-current/10",
    outline:
      "border border-ink/15 bg-paper/60 text-ink backdrop-blur-sm hover:border-indigo hover:text-indigo",
  };

  const classes = cn(base, variants[variant], className);

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
    if (href.startsWith("http") || href.startsWith("tel:")) {
      const external = href.startsWith("http");
      return (
        <a
          href={href}
          className={classes}
          {...(external
            ? { target: "_blank", rel: "noopener noreferrer" }
            : {})}
        >
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