import * as THREE from "three";
import type { FigureKind } from "./figure";

const H = 2.5;

function cloneMat(base: THREE.MeshStandardMaterial) {
  const m = base.clone();
  m.emissive = new THREE.Color(0x000000);
  m.emissiveIntensity = 0;
  return m;
}

function addSegment(
  group: THREE.Group,
  a: THREE.Vector3,
  b: THREE.Vector3,
  r: number,
  zone: string,
  base: THREE.MeshStandardMaterial
) {
  const len = a.distanceTo(b);
  const geo = new THREE.CapsuleGeometry(r, len, 8, 24);
  const mat = cloneMat(base);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.name = zone;
  mesh.userData.zone = zone;
  mesh.position.copy(a).add(b).multiplyScalar(0.5);
  const dir = new THREE.Vector3().subVectors(b, a).normalize();
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
  group.add(mesh);
  return mesh;
}

export function createBodyMapFigure(
  kind: FigureKind,
  base: THREE.MeshStandardMaterial
): THREE.Group {
  const g = new THREE.Group();
  g.name = kind;
  const male = kind === "male";

  const hipY = H * 0.4;
  const hipSpread = male ? 0.082 : 0.09;
  const shoulderY = H * 0.8;
  const shoulderSpread = male ? 0.175 : 0.15;
  const headC = H * 0.92;
  const headR = male ? 0.148 : 0.142;

  // pelvis
  {
    const m = cloneMat(base);
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(H * 0.085, 28, 28), m);
    mesh.name = male ? "belly" : "hips";
    mesh.userData.zone = male ? "belly" : "hips";
    mesh.position.set(0, hipY, 0);
    mesh.scale.set(1, 0.92, 1.12);
    g.add(mesh);
  }

  // buttocks (female only)
  if (!male) {
    const m = cloneMat(base);
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(H * 0.068, 24, 24), m);
    mesh.name = "buttocks";
    mesh.userData.zone = "buttocks";
    mesh.position.set(0, hipY * 0.98, -H * 0.055);
    mesh.scale.set(1.15, 0.9, 0.55);
    g.add(mesh);
  }

  // back plate (male only) — zone "back"
  if (male) {
    const m = cloneMat(base);
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(H * 0.095, 24, 24), m);
    mesh.name = "back";
    mesh.userData.zone = "back";
    mesh.position.set(0, H * 0.58, -H * 0.08);
    mesh.scale.set(1.2, 0.65, 0.35);
    g.add(mesh);
  }

  // torso split: lower (belly) and upper (chest/breasts)
  const torsoMid = H * 0.58;
  const torsoLo = H * 0.4;
  const torsoHi = H * 0.775;

  addSegment(g, new THREE.Vector3(0, torsoLo, 0), new THREE.Vector3(0, torsoMid, 0), male ? 0.125 : 0.11, "belly", base);
  addSegment(g, new THREE.Vector3(0, torsoMid, 0), new THREE.Vector3(0, torsoHi, 0), male ? 0.135 : 0.12, male ? "chest" : "breasts", base);

  // chest mass
  {
    const m = cloneMat(base);
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(male ? 0.14 : 0.135, 28, 28), m);
    mesh.name = male ? "chest" : "breasts";
    mesh.userData.zone = male ? "chest" : "breasts";
    mesh.position.set(0, H * 0.745, 0);
    mesh.scale.set(male ? 1.1 : 0.98, 0.82, 0.96);
    g.add(mesh);
  }

  if (male) {
    for (const side of [-1, 1]) {
      const m = cloneMat(base);
      const mesh = new THREE.Mesh(new THREE.SphereGeometry(H * 0.052, 24, 24), m);
      mesh.name = "chest";
      mesh.userData.zone = "chest";
      mesh.position.set(side * H * 0.085, H * 0.75, H * 0.045);
      mesh.scale.set(1.25, 0.85, 0.6);
      g.add(mesh);
    }
  } else {
    for (const side of [-1, 1]) {
      const m = cloneMat(base);
      const mesh = new THREE.Mesh(new THREE.SphereGeometry(H * 0.052, 24, 24), m);
      mesh.name = "breasts";
      mesh.userData.zone = "breasts";
      mesh.position.set(side * H * 0.06, H * 0.72, H * 0.055);
      mesh.scale.set(1, 0.9, 0.75);
      g.add(mesh);
    }
  }

  // neck
  addSegment(g, new THREE.Vector3(0, H * 0.81, 0), new THREE.Vector3(0, H * 0.875, 0), H * 0.038, male ? "neck" : "face", base);

  // head
  {
    const m = cloneMat(base);
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(headR, 32, 32), m);
    mesh.name = "face";
    mesh.userData.zone = "face";
    mesh.position.set(0, headC, 0);
    mesh.scale.set(male ? 0.94 : 0.92, 1.12, 0.98);
    g.add(mesh);
  }
  {
    const m = cloneMat(base);
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(0.015, 14, 14), m);
    mesh.name = "face";
    mesh.userData.zone = "face";
    mesh.position.set(0, headC - headR * 0.28, headR * 0.98);
    mesh.scale.set(1, 1.4, 0.6);
    g.add(mesh);
  }

  // arms
  const shoulderR = male ? 0.072 : 0.06;
  const handY = H * 0.3;
  const armAngle = male ? 0.16 : 0.14;
  for (const side of [-1, 1]) {
    const s = new THREE.Vector3(side * shoulderSpread, shoulderY, 0);
    {
      const m = cloneMat(base);
      const mesh = new THREE.Mesh(new THREE.SphereGeometry(shoulderR, 22, 22), m);
      mesh.name = male ? "" : "arms";
      mesh.userData.zone = male ? "" : "arms";
      mesh.position.copy(s);
      g.add(mesh);
    }
    const elbow = s.clone().add(new THREE.Vector3(side * armAngle * H * 0.55, -H * 0.3, 0));
    const wrist = new THREE.Vector3(side * armAngle * H * 0.8, handY, 0);
    addSegment(g, s, elbow, H * 0.055, male ? "" : "arms", base);
    addSegment(g, elbow, wrist, H * 0.045, male ? "" : "arms", base);
    {
      const m = cloneMat(base);
      const mesh = new THREE.Mesh(new THREE.SphereGeometry(H * 0.03, 18, 18), m);
      mesh.name = male ? "" : "arms";
      mesh.userData.zone = male ? "" : "arms";
      mesh.position.copy(wrist).add(new THREE.Vector3(0, -H * 0.03, 0));
      g.add(mesh);
    }
  }

  // legs
  for (const side of [-1, 1]) {
    const hip = new THREE.Vector3(side * hipSpread * 1.15, hipY, 0);
    const knee = new THREE.Vector3(side * hipSpread, H * 0.19, 0);
    const ankle = new THREE.Vector3(side * hipSpread * 0.92, H * 0.05, 0);
    addSegment(g, hip, knee, H * 0.06, male ? "belly" : "hips", base);
    addSegment(g, knee, ankle, H * 0.042, male ? "belly" : "hips", base);
    {
      const m = cloneMat(base);
      const mesh = new THREE.Mesh(new THREE.SphereGeometry(H * 0.028, 16, 16), m);
      mesh.name = male ? "belly" : "hips";
      mesh.userData.zone = male ? "belly" : "hips";
      mesh.position.set(side * hipSpread * 0.95, H * 0.035, H * 0.035);
      mesh.scale.set(1.5, 0.55, 1.2);
      g.add(mesh);
    }
  }

  g.scale.setScalar(0.92);
  g.position.y = -0.05;
  return g;
}