export function EcgDivider({
  className = "",
  color = "currentColor",
}: {
  className?: string;
  color?: string;
}) {
  return (
    <span className={`animate-ecg inline-block ${className}`} aria-hidden="true">
      <svg
        viewBox="0 0 120 24"
        className="h-6 w-[120px]"
        fill="none"
        stroke={color}
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M2 12h22l6-9 12 18 10-15 5 6h31" />
      </svg>
    </span>
  );
}

export function PlusMark({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={`size-5 ${className}`}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.4"
      strokeLinecap="round"
      aria-hidden="true"
    >
      <path d="M12 4v16M4 12h16" opacity="0.9" />
      <circle cx="12" cy="12" r="8" opacity="0.35" />
    </svg>
  );
}