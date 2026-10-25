import * as THREE from "three";

export type FigureKind = "female" | "male";

const H = 2.5;

function addSegment(
  group: THREE.Group,
  a: THREE.Vector3,
  b: THREE.Vector3,
  r: number,
  name: string,
  mat: THREE.Material
) {
  const len = a.distanceTo(b);
  const geo = new THREE.CapsuleGeometry(r, len, 8, 28);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.name = name;
  mesh.position.copy(a).add(b).multiplyScalar(0.5);
  const dir = new THREE.Vector3().subVectors(b, a).normalize();
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
  group.add(mesh);
  return mesh;
}

export function createFigure(
  kind: FigureKind,
  material: THREE.Material
): THREE.Group {
  const g = new THREE.Group();
  g.name = kind;
  const male = kind === "male";
  const mat = material;

  const hipY = H * 0.4;
  const hipSpread = male ? 0.082 : 0.09;
  const shoulderY = H * 0.8;
  const shoulderSpread = male ? 0.175 : 0.15;
  const headC = H * 0.92;
  const headR = male ? 0.148 : 0.142;

  const pelvis = new THREE.Mesh(
    new THREE.SphereGeometry(H * 0.085, 32, 32),
    mat
  );
  pelvis.name = "hip";
  pelvis.position.set(0, hipY, 0);
  pelvis.scale.set(1, 0.92, 1.12);
  g.add(pelvis);

  const torsoLo = H * 0.4;
  const torsoHi = H * 0.775;
  addSegment(
    g,
    new THREE.Vector3(0, torsoLo, 0),
    new THREE.Vector3(0, torsoHi, 0),
    male ? 0.13 : 0.115,
    "torso",
    mat
  );

  const chest = new THREE.Mesh(
    new THREE.SphereGeometry(male ? 0.14 : 0.135, 32, 32),
    mat
  );
  chest.name = "chest";
  chest.position.set(0, H * 0.745, 0);
  chest.scale.set(male ? 1.1 : 0.98, 0.82, 0.96);
  g.add(chest);

  if (male) {
    for (const side of [-1, 1]) {
      const pec = new THREE.Mesh(
        new THREE.SphereGeometry(H * 0.052, 28, 28),
        mat
      );
      pec.name = "pectorals";
      pec.position.set(side * H * 0.085, H * 0.75, H * 0.045);
      pec.scale.set(1.25, 0.85, 0.6);
      g.add(pec);
    }
  } else {
    for (const side of [-1, 1]) {
      const breast = new THREE.Mesh(
        new THREE.SphereGeometry(H * 0.052, 28, 28),
        mat
      );
      breast.name = "breasts";
      breast.position.set(side * H * 0.06, H * 0.72, H * 0.055);
      breast.scale.set(1, 0.9, 0.75);
      g.add(breast);
    }
  }

  addSegment(
    g,
    new THREE.Vector3(0, H * 0.81, 0),
    new THREE.Vector3(0, H * 0.875, 0),
    H * 0.038,
    "neck",
    mat
  );

  const head = new THREE.Mesh(new THREE.SphereGeometry(headR, 40, 40), mat);
  head.name = "head";
  head.position.set(0, headC, 0);
  head.scale.set(male ? 0.94 : 0.92, 1.12, 0.98);
  g.add(head);

  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.015, 16, 16), mat);
  nose.name = "nose";
  nose.position.set(0, headC - headR * 0.28, headR * 0.98);
  nose.scale.set(1, 1.4, 0.6);
  g.add(nose);

  const shoulderR = male ? 0.072 : 0.06;
  const handY = H * 0.3;
  const armAngle = male ? 0.16 : 0.14;
  for (const side of [-1, 1]) {
    const s = new THREE.Vector3(side * shoulderSpread, shoulderY, 0);
    const shoulderBall = new THREE.Mesh(
      new THREE.SphereGeometry(shoulderR, 28, 28),
      mat
    );
    shoulderBall.name = "shoulder";
    shoulderBall.position.copy(s);
    g.add(shoulderBall);

    const elbow = s.clone().add(
      new THREE.Vector3(side * armAngle * H * 0.55, -H * 0.3, 0)
    );
    const wrist = new THREE.Vector3(side * armAngle * H * 0.8, handY, 0);
    addSegment(g, s, elbow, H * 0.055, "arm", mat);
    addSegment(g, elbow, wrist, H * 0.045, "forearm", mat);

    const hand = new THREE.Mesh(new THREE.SphereGeometry(H * 0.03, 20, 20), mat);
    hand.name = "hand";
    hand.position.copy(wrist).add(new THREE.Vector3(0, -H * 0.03, 0));
    g.add(hand);
  }

  for (const side of [-1, 1]) {
    const hip = new THREE.Vector3(side * hipSpread * 1.15, hipY, 0);
    const knee = new THREE.Vector3(side * hipSpread, H * 0.19, 0);
    const ankle = new THREE.Vector3(side * hipSpread * 0.92, H * 0.05, 0);
    addSegment(g, hip, knee, H * 0.06, "thigh", mat);
    addSegment(g, knee, ankle, H * 0.042, "shin", mat);

    const foot = new THREE.Mesh(new THREE.SphereGeometry(H * 0.028, 18, 18), mat);
    foot.name = "foot";
    foot.position.set(side * hipSpread * 0.95, H * 0.035, H * 0.035);
    foot.scale.set(1.5, 0.55, 1.2);
    g.add(foot);
  }

  g.scale.setScalar(0.92);
  g.userData.kind = kind;
  return g;
}