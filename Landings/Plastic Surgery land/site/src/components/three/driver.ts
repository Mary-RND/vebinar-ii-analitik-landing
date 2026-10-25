import type { HeroDriver } from "./HeroScene";

/** Драйвер анимации hero: читается в useFrame, пишется из скролла и указателя. */
export const heroDriver: HeroDriver = {
  progress: 0,
  pointer: { x: 0, y: 0 },
};