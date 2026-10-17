"use client";

import { Suspense, useMemo, useRef } from "react";
import { Canvas, useFrame, useLoader } from "@react-three/fiber";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { ContactShadows, Environment, Lightformer } from "@react-three/drei";
import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";
import { useIsMobile } from "@/hooks/useWebGL";

export type HeroDriver = {
  progress: number;
  pointer: { x: number; y: number };
};

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
const MODEL_URL = `${BASE}/models/aphrodite.glb`;

/** Кадрирование фигуры в мировых координатах — снято с прежней лате-версии. */
const FRAMING = {
  desktop: { x: 1.45, centerY: 1.45, height: 2.46 },
  mobile: { x: 0, centerY: -0.232, height: 1.91 },
};

/** Кольца: доли от высоты фигуры (y, радиус, толщина, сдвиг по скроллу). */
const RINGS = [
  { y: 0.29, r: 0.331, tube: 0.0036, spread: -0.097, speed: 0.14, dir: 1 },
  { y: 0.62, r: 0.403, tube: 0.0026, spread: 0.006, speed: 0.2, dir: -1 },
  { y: 0.91, r: 0.299, tube: 0.0026, spread: 0.11, speed: 0.26, dir: 1 },
];

/**
 * Полунеявный Эйлер: масса и инерция вместо линейного lerp.
 * damping чуть ниже критического — фигура слегка «продолжает» движение.
 */
class Spring {
  value: number;
  velocity = 0;

  constructor(value: number) {
    this.value = value;
  }

  step(target: number, dt: number, stiffness = 44, damping = 13) {
    const h = Math.min(dt, 1 / 30);
    this.velocity += ((target - this.value) * stiffness - this.velocity * damping) * h;
    this.value += this.velocity * h;
    return this.value;
  }
}

let marble: THREE.MeshPhysicalMaterial | null = null;

function marbleMaterial() {
  if (!marble) {
    marble = new THREE.MeshPhysicalMaterial({
      color: "#e6eaf4",
      roughness: 0.5,
      metalness: 0,
      clearcoat: 0.45,
      clearcoatRoughness: 0.32,
      envMapIntensity: 0.55,
    });
  }
  return marble;
}

function Lights({ mobile }: { mobile: boolean }) {
  const map = mobile ? 512 : 2048;
  return (
    <>
      <ambientLight intensity={0.26} color="#e8ecff" />
      <directionalLight
        castShadow
        position={[4, 6, 5]}
        intensity={1.35}
        color="#ffffff"
        shadow-mapSize-width={map}
        shadow-mapSize-height={map}
        shadow-camera-left={-2.5}
        shadow-camera-right={3.5}
        shadow-camera-top={3.5}
        shadow-camera-bottom={-2.5}
        shadow-camera-near={2}
        shadow-camera-far={18}
        shadow-bias={-0.0004}
        shadow-normalBias={0.015}
      />
      <directionalLight position={[-5, 2.5, -4]} intensity={0.9} color="#8f8ce8" />
      <directionalLight position={[5, 2, -4.5]} intensity={0.85} color="#5ec8e4" />
      <pointLight position={[0, 1.2, 3.6]} intensity={0.25} color="#ffffff" />
    </>
  );
}

function Dust() {
  const geometry = useMemo(() => {
    let seed = 20260104;
    const rnd = () => {
      seed = (seed * 1664525 + 1013904223) % 4294967296;
      return seed / 4294967296;
    };
    const count = 260;
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 1.6 + rnd() * 3.4;
      const a = rnd() * Math.PI * 2;
      arr[i * 3] = Math.cos(a) * r;
      arr[i * 3 + 1] = rnd() * 4.2 - 0.3;
      arr[i * 3 + 2] = Math.sin(a) * r * 0.7 - 1.2;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(arr, 3));
    return g;
  }, []);

  const points = useRef<THREE.Points>(null);

  useFrame((state) => {
    if (points.current) points.current.rotation.y = state.clock.elapsedTime * 0.05;
  });

  return (
    <points ref={points} geometry={geometry}>
      <pointsMaterial
        size={0.022}
        color="#c9cffb"
        transparent
        opacity={0.5}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  );
}

function Statue({ driver, mobile }: { driver: HeroDriver; mobile: boolean }) {
  const gltf = useLoader(GLTFLoader, MODEL_URL);
  const outer = useRef<THREE.Group>(null);
  const spin = useRef<THREE.Group>(null);
  const ground = useRef<THREE.Group>(null);
  const ringRefs = useRef<Array<THREE.Mesh | null>>([]);

  const fit = useMemo(() => {
    const scene = gltf.scene;
    scene.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(scene);
    const size = box.getSize(new THREE.Vector3());
    const material = marbleMaterial();
    scene.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (!mesh.isMesh) return;
      mesh.material = material;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
    });
    return { h: Math.max(0.001, size.y) };
  }, [gltf]);

  const springs = useMemo(() => {
    const start = FRAMING.desktop;
    return {
      x: new Spring(start.x),
      y: new Spring(start.centerY - start.height / 2),
      scale: new Spring(start.height / fit.h),
      rot: new Spring(0),
      e: new Spring(0),
      camX: new Spring(0),
      camY: new Spring(1.5),
      camZ: new Spring(5.4),
      rings: RINGS.map((r) => new Spring(r.y * fit.h)),
    };
  }, [fit.h]);

  useFrame((state, delta) => {
    const dt = Math.min(delta, 1 / 30);
    const t = state.clock.elapsedTime;
    const f = mobile ? FRAMING.mobile : FRAMING.desktop;
    const px = driver.pointer.x;
    const py = driver.pointer.y;

    const step = Math.min(1, Math.max(0, driver.progress));
    const eased = step * step * (3 - 2 * step);
    const e = springs.e.step(eased, dt, 38, 12);

    const x = springs.x.step(f.x + px * 0.05, dt, 40, 12.5);
    const y = springs.y.step(
      f.centerY - f.height / 2 + Math.sin(t * 0.6) * 0.018,
      dt,
      40,
      12.5
    );
    const scale = springs.scale.step(f.height / fit.h, dt, 40, 12.5);

    if (outer.current) {
      outer.current.position.set(x, y, 0);
      outer.current.scale.setScalar(scale);
    }
    if (ground.current) ground.current.position.set(x, y + 0.004, 0);

    if (spin.current) {
      const target = Math.sin(t * 0.24) * 0.16 + px * 0.18 + e * 2.2;
      spin.current.rotation.y = springs.rot.step(target, dt, 34, 11);
    }

    RINGS.forEach((ring, i) => {
      const mesh = ringRefs.current[i];
      if (!mesh) return;
      mesh.position.y = springs.rings[i].step((ring.y + e * ring.spread) * fit.h, dt, 40, 12.5);
      mesh.rotation.z = t * ring.speed * ring.dir;
      mesh.rotation.x = Math.PI / 2 + Math.sin(t * 0.3 + i) * 0.16;
    });

    const cx = springs.camX.step(px * 0.42, dt, 26, 10);
    const cy = springs.camY.step(1.5 + py * 0.26, dt, 26, 10);
    const cz = springs.camZ.step(5.4 + e * 1.1, dt, 26, 10);
    state.camera.position.set(cx, cy, cz);
    state.camera.lookAt(0, 1.45, 0);
  });

  return (
    <>
      <group ref={outer} position={[FRAMING.desktop.x, 0.22, 0]} scale={2.56}>
        <group ref={spin}>
          <primitive object={gltf.scene} />
        </group>

        {RINGS.map((ring, i) => (
          <mesh
            key={i}
            ref={(node) => {
              ringRefs.current[i] = node;
            }}
            position={[0, ring.y * fit.h, 0]}
          >
            <torusGeometry args={[ring.r * fit.h, ring.tube, 12, 160]} />
            <meshStandardMaterial
              color="#5ec8e4"
              emissive="#2b7f96"
              emissiveIntensity={0.55}
              roughness={0.35}
              metalness={0.2}
            />
          </mesh>
        ))}
      </group>

      <group ref={ground}>
        <ContactShadows
          position={[0, 0, 0]}
          scale={2.8}
          blur={2.6}
          opacity={0.55}
          far={1.3}
          resolution={mobile ? 256 : 512}
          color="#05070f"
        />
      </group>

      <Environment resolution={256} frames={1}>
        <Lightformer intensity={1.1} position={[0, 3, 4]} scale={[7, 4, 1]} color="#ffffff" />
        <Lightformer intensity={0.6} position={[-5, 1, -3]} scale={[6, 6, 1]} color="#8f8ce8" />
        <Lightformer intensity={0.7} position={[5, 2, -3]} scale={[6, 6, 1]} color="#5ec8e4" />
        <Lightformer
          form="ring"
          intensity={0.9}
          position={[2, 5, 2]}
          scale={3}
          color="#ffffff"
        />
        <Lightformer intensity={0.5} position={[0, 0, 12]} scale={[40, 40, 1]} color="#9aa6d6" />
        <Lightformer intensity={0.4} position={[0, 0, -12]} scale={[40, 40, 1]} color="#6b74a8" />
        <Lightformer intensity={0.45} position={[0, 12, 0]} scale={[30, 30, 1]} color="#c8d2f2" />
        <Lightformer intensity={0.3} position={[0, -12, 0]} scale={[30, 30, 1]} color="#3a4270" />
      </Environment>
    </>
  );
}

export function HeroScene({ driver }: { driver: HeroDriver }) {
  const mobile = useIsMobile() === true;

  return (
    <Canvas
      shadows={!mobile}
      camera={{ position: [0, 1.5, 5.4], fov: 34, near: 0.1, far: 40 }}
      gl={{
        antialias: true,
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 0.94,
      }}
      dpr={mobile ? [1, 1.5] : [1, 1.8]}
    >
      <color attach="background" args={["#141a30"]} />
      <fog attach="fog" args={["#141a30", 7.5, 16]} />

      <Suspense fallback={null}>
        <Statue driver={driver} mobile={mobile} />
      </Suspense>

      <Dust />
      <Lights mobile={mobile} />

      <EffectComposer>
        <Bloom intensity={0.35} luminanceThreshold={0.92} mipmapBlur />
        <Vignette offset={0.24} darkness={0.6} />
      </EffectComposer>
    </Canvas>
  );
}
