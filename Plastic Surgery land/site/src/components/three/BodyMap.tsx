"use client";

import { bodyZones, type BodyZone } from "@/lib/site";

type Props = {
  active: string;
  onSelect: (zone: BodyZone) => void;
};

export function BodyMap({ active, onSelect }: Props) {
  return (
    <figure className="relative mx-auto w-full max-w-sm">
      <svg
        viewBox="0 0 200 400"
        className="h-auto w-full"
        role="img"
        aria-label="Схема тела с зонами пластических операций"
      >
        <defs>
          <linearGradient id="body-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#dce8f7" />
            <stop offset="55%" stopColor="#c8d8ef" />
            <stop offset="100%" stopColor="#b9cdf0" />
          </linearGradient>
          <linearGradient id="body-line" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#4348c8" />
            <stop offset="100%" stopColor="#5ec8e4" />
          </linearGradient>
        </defs>

        <g
          fill="url(#body-fill)"
          stroke="#4348c8"
          strokeOpacity="0.28"
          strokeWidth="1"
        >
          <ellipse cx="100" cy="44" rx="18" ry="21" />
          <rect x="91" y="60" width="18" height="18" rx="6" />
          <path d="M100 74 C126 74 140 84 144 104 C147 124 141 136 137 150 C134 160 132 168 133 182 C150 187 160 198 160 214 C160 232 148 242 134 244 L66 244 C52 242 40 232 40 214 C40 198 50 187 67 182 C68 168 66 160 63 150 C59 136 53 124 56 104 C60 84 74 74 100 74 Z" />
          <path d="M58 92 C48 118 44 152 46 186 C47 200 52 206 58 204 C64 202 66 194 65 182 C63 152 66 124 72 104 Z" />
          <path d="M142 92 C152 118 156 152 154 186 C153 200 148 206 142 204 C136 202 134 194 135 182 C137 152 134 124 128 104 Z" />
          <path d="M70 240 C64 268 60 300 58 330 C57 352 58 372 60 388 L86 388 C88 368 90 344 92 322 C94 296 96 266 96 242 Z" />
          <path d="M130 240 C136 268 140 300 142 330 C143 352 142 372 140 388 L114 388 C112 368 110 344 108 322 C106 296 104 266 104 242 Z" />
        </g>

        <g fill="none" stroke="url(#body-line)" strokeOpacity="0.35" strokeWidth="0.8">
          <path d="M100 104 C112 108 128 108 140 104" />
          <path d="M100 150 C112 154 126 154 136 150" />
          <path d="M100 186 C112 190 126 190 138 186" />
          <path d="M78 120 C86 126 96 126 100 122" />
          <path d="M122 120 C114 126 104 126 100 122" />
        </g>

        {bodyZones.map((z) => {
          const on = z.id === active;
          return (
            <g key={z.id}>
              <circle
                cx={z.x}
                cy={z.y}
                r={on ? 11 : 7}
                fill={on ? "#4348c8" : "#ffffff"}
                fillOpacity={on ? 0.9 : 1}
                stroke={on ? "#5ec8e4" : "#4348c8"}
                strokeOpacity={on ? 1 : 0.45}
                strokeWidth="1.5"
                className="transition-all duration-300"
              />
              {on && (
                <circle
                  cx={z.x}
                  cy={z.y}
                  r="16"
                  fill="none"
                  stroke="#5ec8e4"
                  strokeOpacity="0.55"
                  strokeWidth="1"
                  className="animate-pulse-ring"
                />
              )}
              <circle
                cx={z.x}
                cy={z.y}
                r="14"
                fill="transparent"
                className="cursor-pointer"
                tabIndex={0}
                role="button"
                aria-label={z.label}
                aria-pressed={on}
                onClick={() => onSelect(z)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onSelect(z);
                  }
                }}
              />
            </g>
          );
        })}
      </svg>

      <figcaption className="mt-4 text-center text-xs text-slate">
        Нажмите на точку, чтобы увидеть операции в этой зоне
      </figcaption>
    </figure>
  );
}