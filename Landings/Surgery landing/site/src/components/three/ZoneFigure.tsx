"use client";

import { useMemo, useRef, useState } from "react";
import {
  Canvas,
  useFrame,
  useThree,
  type ThreeEvent,
} from "@react-three/fiber";
import * as THREE from "three";
import { createBodyMapFigure } from "./bodyMapFigure";

export type Zone = { id: string; label: string; hint: string };

function ZoneRig({
  kind,
  accent,
  zones,
  onHover,
  onPick,
  camY = 1.15,
  camZ = 5.6,
}: {
  kind: "female" | "male";
  accent: string;
  zones: Zone[];
  onHover: (z: Zone | null) => void;
  onPick: (z: Zone) => void;
  camY?: number;
  camZ?: number;
}) {
  const byId = useMemo(
    () => Object.fromEntries(zones.map((z) => [z.id, z])),
    [zones]
  );
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
  const figure = useMemo(
    () => createBodyMapFigure(kind, baseMat),
    [kind, baseMat]
  );
  const { camera, raycaster, pointer } = useThree();

  const meshes = useMemo(() => {
    const out: THREE.Mesh[] = [];
    figure.traverse((o: THREE.Object3D) => {
      if ((o as THREE.Mesh).isMesh) out.push(o as THREE.Mesh);
    });
    return out;
  }, [figure]);

  const accentColor = useMemo(() => new THREE.Color(accent), [accent]);
  const baseColor = useMemo(() => new THREE.Color(0x000000), []);
  const hoveredRef = useRef<string | null>(null);

  const handleZoneClick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    const zoneId = (e.object as unknown as { userData?: { zone?: string } })
      .userData?.zone;
    if (!zoneId) return;
    const z = byId[zoneId];
    if (z) onPick(z);
  };

  useFrame((state, delta) => {
    const g = groupRef.current;
    if (g) {
      const t = state.clock.elapsedTime;
      g.rotation.y = Math.sin(t * 0.35) * 0.45;
      g.rotation.x = THREE.MathUtils.lerp(g.rotation.x, pointer.y * 0.1, 0.05);
      g.position.y = -0.05 + Math.sin(t * 0.9) * 0.018;
      camera.lookAt(0, 1.08, 0);

      raycaster.setFromCamera(pointer, camera);
      const hits = raycaster.intersectObject(g, true);
      let zone: Zone | null = null;
      if (hits.length) {
        const hit = hits[0].object as THREE.Mesh & {
          userData: { zone?: string };
        };
        const id = hit.userData.zone;
        if (id && byId[id]) zone = byId[id];
      }

      const id = zone?.id ?? null;
      if (id !== hoveredRef.current) {
        hoveredRef.current = id;
        onHover(zone);
        state.gl.domElement.style.cursor = zone ? "pointer" : "auto";
      }

      const k = Math.min(1, delta * 6);
      for (const m of meshes) {
        const mat = m.material as THREE.MeshStandardMaterial;
        const isActive = Boolean(id && m.userData.zone === id);
        mat.emissive.lerp(isActive ? accentColor : baseColor, k);
        mat.emissiveIntensity = THREE.MathUtils.lerp(
          mat.emissiveIntensity,
          isActive ? 0.9 : 0,
          k
        );
      }
    }
  });

  return (
    <>
      <ambientLight intensity={0.6} color="#fff6ea" />
      <directionalLight position={[3, 5, 4]} intensity={1.15} color="#fff2df" />
      <directionalLight
        position={[-3, 4, -4]}
        intensity={0.9}
        color={accent}
      />
      <group ref={groupRef} position={[0, -0.05, 0]} scale={0.92}>
        {meshes.map((m) => (
          <primitive
            key={m.uuid}
            object={m}
            onClick={handleZoneClick}
          />
        ))}
      </group>
    </>
  );
}

export function ZoneFigure({
  kind,
  accent,
  zones,
  className = "h-[420px]",
  onPick,
  defaultHoverLabel = "Наведите курсор на зону, чтобы узнать о возможностях",
  camY = 1.15,
  camZ = 5.6,
}: {
  kind: "female" | "male";
  accent: string;
  zones: Zone[];
  className?: string;
  onPick?: (z: Zone) => void;
  defaultHoverLabel?: string;
  camY?: number;
  camZ?: number;
}) {
  const [hovered, setHovered] = useState<Zone | null>(null);

  return (
    <div className={`relative overflow-hidden ${className}`}>
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(58% 46% at 50% 80%, rgba(184,115,79,0.20), transparent 72%)",
        }}
      />
      <div
        aria-hidden="true"
        className="medical-dots pointer-events-none absolute inset-0 text-ink/10"
      />
      <Canvas
        camera={{ position: [0, camY, camZ], fov: 26, near: 0.1, far: 20 }}
        gl={{
          antialias: true,
          alpha: true,
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.08,
        }}
        dpr={[1, 1.6]}
        style={{ background: "transparent" }}
      >
        <ZoneRig
          kind={kind}
          accent={accent}
          zones={zones}
          onHover={setHovered}
          onPick={(z) => onPick?.(z)}
          camY={camY}
          camZ={camZ}
        />
      </Canvas>
      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex justify-center p-3">
        <div className="max-w-[92%] rounded-full bg-white/90 px-4 py-2 text-center text-xs font-medium text-ink/70 shadow-sm ring-1 ring-ink/10 backdrop-blur">
          {hovered ? (
            <span>
              <span style={{ color: accent }}>{hovered.hint}</span>
              <span className="text-ink/40"> — </span>
              {hovered.label}. Нажмите, чтобы узнать детали.
            </span>
          ) : (
            <span>{defaultHoverLabel}</span>
          )}
        </div>
      </div>
    </div>
  );
}