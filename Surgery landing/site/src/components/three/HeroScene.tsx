"use client";

import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";
import { createFigure } from "./figure";

export type HeroDriver = {
  progress: number;
  pointer: { x: number; y: number };
};

function StatueRig({ driver }: { driver: HeroDriver }) {
  const full = useRef<THREE.Group>(null);
  const female = useRef<THREE.Group>(null);
  const male = useRef<THREE.Group>(null);

  const materials = useMemo(() => {
    const femaleMat = new THREE.MeshStandardMaterial({
      color: "#ede6d8",
      roughness: 0.42,
      metalness: 0.05,
    });
    const maleMat = new THREE.MeshStandardMaterial({
      color: "#262b2f",
      roughness: 0.38,
      metalness: 0.07,
    });
    const pedestalMat = new THREE.MeshStandardMaterial({
      color: "#2e3339",
      roughness: 0.55,
      metalness: 0.1,
    });
    const groundMat = new THREE.MeshStandardMaterial({
      color: "#17191c",
      roughness: 0.85,
      metalness: 0,
    });
    return { femaleMat, maleMat, pedestalMat, groundMat };
  }, []);

  const femaleGroup = useMemo(
    () => createFigure("female", materials.femaleMat),
    [materials]
  );
  const maleGroup = useMemo(
    () => createFigure("male", materials.maleMat),
    [materials]
  );

  useFrame((state, delta) => {
    const t = state.clock.elapsedTime;
    const step = Math.min(1, Math.max(0, driver.progress));
    const ease = Math.min(1, delta * 2.4);

    if (full.current) {
      const idle = t * 0.22;
      full.current.rotation.y = THREE.MathUtils.lerp(
        full.current.rotation.y,
        idle * (1 - step) * (1 - step),
        ease
      );
    }

    if (female.current) {
      const targetSpin = step > 0.4 ? 0 : Math.sin(t * 0.9) * 0.55;
      female.current.rotation.y = THREE.MathUtils.lerp(
        female.current.rotation.y,
        targetSpin,
        ease
      );
      const tx = THREE.MathUtils.lerp(-0.62, -2.35, step);
      female.current.position.x = THREE.MathUtils.lerp(
        female.current.position.x,
        tx,
        ease
      );
      female.current.position.y =
        Math.sin(t * 1.15) * 0.04 + step * 0.05;
      female.current.position.z = THREE.MathUtils.lerp(
        female.current.position.z,
        step * 0.5,
        ease
      );
    }

    if (male.current) {
      const targetSpin =
        step > 0.4 ? 0 : Math.sin(t * 0.9 + Math.PI) * 0.55;
      male.current.rotation.y = THREE.MathUtils.lerp(
        male.current.rotation.y,
        targetSpin,
        ease
      );
      const tx = THREE.MathUtils.lerp(0.62, 2.35, step);
      male.current.position.x = THREE.MathUtils.lerp(
        male.current.position.x,
        tx,
        ease
      );
      male.current.position.y =
        Math.sin(t * 1.15 + Math.PI * 0.6) * 0.04 + step * 0.05;
      male.current.position.z = THREE.MathUtils.lerp(
        male.current.position.z,
        step * 0.5,
        ease
      );
    }

    const cam = state.camera;
    const c = ease * 0.6;
    cam.position.x = THREE.MathUtils.lerp(
      cam.position.x,
      driver.pointer.x * 0.5,
      c
    );
    cam.position.y = THREE.MathUtils.lerp(
      cam.position.y,
      1.18 + driver.pointer.y * 0.3,
      c
    );
    cam.position.z = THREE.MathUtils.lerp(
      cam.position.z,
      6.3 - step * 1.1,
      c
    );
    cam.lookAt(0, 1.12, 0);
  });

  return (
    <>
      <color attach="background" args={["#1f2326"]} />
      <fog attach="fog" args={["#1f2326", 9, 18]} />

      <group ref={full}>
        <group ref={female} position={[-0.62, 0, 0]}>
          <primitive object={femaleGroup} />
          <mesh position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.5, 0.54, 0.045, 64]} />
            <primitive object={materials.pedestalMat} attach="material" />
          </mesh>
        </group>

        <group ref={male} position={[0.62, 0, 0]}>
          <primitive object={maleGroup} />
          <mesh position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.5, 0.54, 0.045, 64]} />
            <primitive object={materials.pedestalMat} attach="material" />
          </mesh>
        </group>
      </group>

      <mesh position={[0, -0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[9, 64]} />
        <meshStandardMaterial {...materials.groundMat} />
      </mesh>

      <ambientLight intensity={0.28} color="#fff6ea" />
      <directionalLight position={[3.5, 6, 4]} intensity={1.5} color="#fff2df" />
      <directionalLight position={[-4.5, 3, -5]} intensity={2.4} color="#b8734f" />
      <directionalLight position={[4.5, 3, -5]} intensity={2.2} color="#c79353" />
      <pointLight position={[0, -2, 3.5]} intensity={0.35} color="#ffffff" />
    </>
  );
}

export function HeroScene({ driver }: { driver: HeroDriver }) {
  return (
    <Canvas
      camera={{ position: [0, 1.18, 6.3], fov: 36, near: 0.1, far: 40 }}
      gl={{
        antialias: true,
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.12,
      }}
      dpr={[1, 1.8]}
    >
      <StatueRig driver={driver} />
      <EffectComposer>
        <Bloom intensity={0.45} luminanceThreshold={1} mipmapBlur />
        <Vignette offset={0.22} darkness={0.55} />
      </EffectComposer>
    </Canvas>
  );
}