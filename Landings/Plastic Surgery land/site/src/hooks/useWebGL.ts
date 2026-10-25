"use client";

import { useSyncExternalStore } from "react";

const emptySubscribe = () => () => {};

let webglSnapshot: boolean | null = null;

function readWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(
      canvas.getContext("webgl2") || canvas.getContext("webgl")
    );
  } catch {
    return false;
  }
}

function getWebGL() {
  if (webglSnapshot === null) webglSnapshot = readWebGL();
  return webglSnapshot;
}

export function useWebGL(): boolean | null {
  return useSyncExternalStore(emptySubscribe, getWebGL, () => null);
}

const mobileQuery = "(max-width: 768px)";

let mobileSnapshot: boolean | null = null;

function getIsMobile() {
  if (mobileSnapshot === null) {
    mobileSnapshot = window.matchMedia(mobileQuery).matches;
  }
  return mobileSnapshot;
}

function subscribeViewport(callback: () => void) {
  const mq = window.matchMedia(mobileQuery);
  const handler = () => {
    mobileSnapshot = mq.matches;
    callback();
  };
  mq.addEventListener("change", handler);
  window.addEventListener("resize", handler);
  return () => {
    mq.removeEventListener("change", handler);
    window.removeEventListener("resize", handler);
  };
}

export function useIsMobile(): boolean | null {
  return useSyncExternalStore(subscribeViewport, getIsMobile, () => null);
}