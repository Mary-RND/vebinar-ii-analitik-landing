"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { createBodyMapFigure } from "./three/bodyMapFigure";
import { femaleBodyZones, maleBodyZones } from "@/lib/site";

type Zone = { id: string; label: string; hint: string };

function Rig({
  kind,
  accent,
  onHover,
  onPick,
}: {
  kind: "female" | "male";
  accent: string;
  onHover: (z: Zone | null) => void;
  onPick: (z: Zone) => void;
}) {
  const zones: Zone[] = kind === "female" ? femaleBodyZones : maleBodyZones;
  const byId = useMemo(() => Object.fromEntries(zones.map((z) => [z.id, z])), [zones]);
  const groupRef = useRef<THREE.Group>(null);
  const baseMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: kind === "female" ? "#ede6d8" : "#23272a",
        roughness: 0.42,
        metalness: 0.05,
      }),
    [kind]
  );
  const figure = useMemo(() => createBodyMapFigure(kind, baseMat), [kind, baseMat]);
  const { camera, raycaster, pointer, gl } = useThree();
  const hovered = useRef<string | null>(null);

  // collect meshes for highlight
  const meshes = useMemo(() => {
    const out: THREE.Mesh[] = [];
    figure.traverse((o: THREE.Object3D) => {
      if ((o as THREE.Mesh).isMesh) out.push(o as THREE.Mesh);
    });
    return out;
  }, [figure]);

  const accentColor = useMemo(() => new THREE.Color(accent), [accent]);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.35) * 0.45;
    }

    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster.intersectObject(figure, true);
    let zone: Zone | null = null;
    if (hits.length) {
      const hit = hits[0].object as THREE.Mesh & { userData: { zone?: string } };
      const id = hit.userData.zone;
      if (id && byId[id]) zone = byId[id];
    }

    const id = zone?.id ?? null;
    if (id !== hovered.current) {
      hovered.current = id;
      onHover(zone);
      gl.domElement.style.cursor = zone ? "pointer" : "auto";
    }

    for (const m of meshes) {
      const mat = m.material as THREE.MeshStandardMaterial;
      const isActive = Boolean(id && (m.userData.zone === id || (id === "hips" && m.userData.zone === "buttocks") || (id === "buttocks" && m.userData.zone === "hips")));
      // also highlight related: breasts <-> chest alias not needed separately
      const target = isActive ? accentColor : new THREE.Color(0x000000);
      mat.emissive.lerp(target, 0.18);
      mat.emissiveIntensity = THREE.MathUtils.lerp(mat.emissiveIntensity, isActive ? 0.85 : 0, 0.18);
    }
  });

  useEffect(() => {
    const el = gl.domElement;
    const onClick = () => {
      if (hovered.current && byId[hovered.current]) onPick(byId[hovered.current]);
    };
    el.addEventListener("click", onClick);
    return () => el.removeEventListener("click", onClick);
  }, [gl, byId, onPick]);

  return (
    <>
      <ambientLight intensity={0.6} color="#fff6ea" />
      <directionalLight position={[3, 5, 4]} intensity={1.15} color="#fff2df" />
      <directionalLight position={[-3, 4, -4]} intensity={0.9} color={accent} />
      <primitive object={figure} ref={groupRef} />
    </>
  );
}

function BodyMapCanvas({
  kind,
  accent,
  onHover,
  onPick,
}: {
  kind: "female" | "male";
  accent: string;
  onHover: (z: Zone | null) => void;
  onPick: (z: Zone) => void;
}) {
  return (
    <Canvas
      camera={{ position: [0, 1.05, 3.9], fov: 26, near: 0.1, far: 20 }}
      gl={{ antialias: true, alpha: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.08 }}
      dpr={[1, 1.6]}
      style={{ background: "transparent" }}
    >
      <Rig kind={kind} accent={accent} onHover={onHover} onPick={onPick} />
    </Canvas>
  );
}

function Card({
  kind,
  title,
  subtitle,
  accent,
  hrefBase,
}: {
  kind: "female" | "male";
  title: string;
  subtitle: string;
  accent: string;
  hrefBase: string;
}) {
  const [hovered, setHovered] = useState<Zone | null>(null);
  const [picked, setPicked] = useState<Zone | null>(null);

  return (
    <div className={kind === "female" ? "rounded-[28px] bg-white p-6 shadow-[0_20px_60px_-30px_rgba(42,40,37,0.22)] sm:p-8" : "rounded-[28px] bg-graphite p-6 text-ivory shadow-[0_20px_60px_-30px_rgba(0,0,0,0.5)] sm:p-8"}>
      <div className="flex items-center gap-3">
        <span className="size-2 rounded-full" style={{ background: accent }} />
        <p className="eyebrow" style={{ color: accent }}>{title}</p>
      </div>
      <h3 className="mt-3 font-display text-2xl font-medium">{kind === "female" ? "Женское тело" : "Мужское тело"}</h3>
      <p className={kind === "female" ? "mt-2 text-sm leading-relaxed text-ink/60" : "mt-2 text-sm leading-relaxed text-ivory/60"}>{subtitle}</p>

      <div className="relative mt-6 overflow-hidden rounded-2xl border border-ink/5 bg-marble" style={kind === "male" ? { background: "rgba(237,230,216,0.06)", borderColor: "rgba(237,230,216,0.12)" } : undefined}>
        <div className="h-[380px] sm:h-[420px]">
          <BodyMapCanvas kind={kind} accent={accent} onHover={setHovered} onPick={setPicked} />
        </div>
        <div className="pointer-events-none absolute inset-x-0 bottom-0 flex justify-center p-3">
          <div className="rounded-full bg-white/90 px-4 py-2 text-xs font-medium text-ink/70 shadow-sm ring-1 ring-ink/10 backdrop-blur">
            {hovered ? (
              <span>
                <span style={{ color: accent }}>{hovered.hint}</span>
                <span className="text-ink/40"> — </span>
                {hovered.label}. Нажмите, чтобы узнать детали.
              </span>
            ) : (
              <span>Наведите курсор на зону, чтобы узнать о возможностях</span>
            )}
          </div>
        </div>
      </div>

      <p className={kind === "female" ? "mt-4 text-xs text-ink/40" : "mt-4 text-xs text-ivory/40"}>
        На мобильных — коснитесь зоны.
      </p>

      {picked && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50 p-5 backdrop-blur-sm" onClick={() => setPicked(null)}>
          <div
            className="w-full max-w-md rounded-2xl bg-white p-8 text-ink shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="eyebrow text-bronze">Вы выбрали направление</p>
            <h4 className="mt-2 font-display text-2xl font-medium">{picked.label}</h4>
            <p className="mt-2 text-sm leading-relaxed text-ink/60">
              Здесь вы найдёте подробное описание метода, реабилитации и ответов на частые
              вопросы.
            </p>
            <div className="mt-6 flex gap-3">
              <a
                href={hrefBase}
                className="inline-flex items-center gap-2 rounded-full bg-terracotta px-6 py-3 text-sm font-semibold text-ivory hover:bg-bronze"
              >
                Перейти к описанию <span aria-hidden>→</span>
              </a>
              <button onClick={() => setPicked(null)} className="rounded-full border border-ink/15 px-6 py-3 text-sm font-semibold hover:bg-ink/5">
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function BodyMaps() {
  return (
    <section id="napravleniya" className="bg-sand/40">
      <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-28">
        <div className="mx-auto max-w-2xl text-center">
          <p className="eyebrow text-bronze">Направления</p>
          <h2 className="mt-4 font-display text-3xl font-medium sm:text-5xl">Выберите направление</h2>
          <p className="mt-4 text-sm text-ink/55">Каждая зона — это отдельная история. Нажмите на область, чтобы узнать, какие решения возможны именно там.</p>
        </div>
        <div className="mt-12 grid gap-6 lg:grid-cols-2">
          <Card
            kind="female"
            title="Женская пластика"
            subtitle="Грудь · Живот · Бёдра · Ягодицы · Руки · Лицо"
            accent="#b8734f"
            hrefBase="/poslerodovoe-vosstanovlenie"
          />
          <Card
            kind="male"
            title="Мужская пластика"
            subtitle="Грудь · Живот · Спина · Лицо · Шея"
            accent="#8b6f47"
            hrefBase="/muzhskaya-plastika"
          />
        </div>
      </div>
    </section>
  );
}