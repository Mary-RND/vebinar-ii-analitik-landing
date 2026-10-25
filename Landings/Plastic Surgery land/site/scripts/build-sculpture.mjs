/**
 * Собирает public/models/aphrodite.glb из assets/aphrodite.stl.
 *
 * Источник: "Statue of Aphrodite with dolphin", 3D photogrammetry scan,
 * Wikimedia Commons, CC BY-SA 4.0.
 *
 * Конвейер: Z-up -> Y-up, срез по горизонтальной плоскости (убирает
 * скалу-постамент), заглушка контуров сечения, склейка вершин, оставляем
 * главную оболочку, центрирование, экспорт GLB вручную (без генераторов).
 *
 * Режимы:
 *   node scripts/build-sculpture.mjs --profile    отчёт профиля, без записи
 *   node scripts/build-sculpture.mjs --analyze    разбор оболочек, без записи
 *   node scripts/build-sculpture.mjs              сборка
 *   CROP_RATIO=0.39 KEEP_LARGEST=0 node ...       переопределение параметров
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import * as THREE from "three";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import { mergeVertices } from "three/examples/jsm/utils/BufferGeometryUtils.js";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SRC = resolve(ROOT, "assets/aphrodite.stl");
const OUT_DIR = resolve(ROOT, "public/models");
const OUT = resolve(OUT_DIR, "aphrodite.glb");

/** Доля высоты скана снизу, приходящаяся на скалу-постамент. */
const CROP_RATIO = Number(process.env.CROP_RATIO ?? 0.41);
/** Оставлять ли только самую большую связную оболочку. */
const KEEP_LARGEST = process.env.KEEP_LARGEST !== "0";
const PROFILE_ONLY = process.argv.includes("--profile");
const ANALYZE = process.argv.includes("--analyze");

if (!existsSync(SRC)) {
  console.error(`[sculpture] нет источника: ${SRC}`);
  process.exit(1);
}

const t0 = Date.now();
const file = readFileSync(SRC);
const buffer = file.buffer.slice(file.byteOffset, file.byteOffset + file.byteLength);
const raw = new STLLoader().parse(buffer);
const rawTris = raw.attributes.position.count / 3;

// Фотограмметрия даёт ось Z вверх.
raw.rotateX(-Math.PI / 2);
raw.computeBoundingBox();
const box0 = raw.boundingBox;
const height0 = box0.max.y - box0.min.y;
const cropY = box0.min.y + height0 * CROP_RATIO;

reportProfile(raw, box0, height0, cropY, rawTris, PROFILE_ONLY);

if (ANALYZE) {
  const full = mergeVertices(positionOnly(raw), 1e-4);
  const { roots, comps } = analyzeComponents(full);
  comps.sort((a, b) => b.tris - a.tris);
  console.log(`[analyze] вершин ${full.attributes.position.count}, оболочек ${comps.length}`);
  for (const c of comps.slice(0, 8)) {
    const slice = keepComponent(full, roots, c.root);
    slice.computeBoundingBox();
    const b = slice.boundingBox;
    console.log(
      `   оболочка: ${c.tris} трис, bbox ${fmt(b)}, y=[${b.min.y.toFixed(3)}..${b.max.y.toFixed(3)}]`
    );
  }
  const rest = comps.slice(8).reduce((sum, c) => sum + c.tris, 0);
  console.log(`   остальных ${Math.max(0, comps.length - 8)} оболочек: ${rest} трис суммарно`);
  process.exit(0);
}

// --- срез по плоскости y >= cropY --------------------------------------------
const clipped = clipAbove(raw, cropY);
console.log(
  `[sculpture] срез y=${cropY.toFixed(3)}: осталось ${clipped.tris} трис, ` +
    `срезано ${clipped.cut}, убрано целиком ${clipped.dropped}`
);

if (clipped.tris === 0) {
  console.error("[sculpture] после среза не осталось геометрии");
  process.exit(1);
}

// --- склейка дублирующихся вершин --------------------------------------------
const merged = mergeVertices(clipped.geometry, 1e-4);
console.log(
  `[sculpture] склейка: ${merged.attributes.position.count} вершин, ${merged.index.count / 3} трис`
);

// --- оставляем главную оболочку -----------------------------------------------
let geometry = merged;
if (KEEP_LARGEST) {
  const { roots, comps } = analyzeComponents(merged);
  comps.sort((a, b) => b.tris - a.tris);
  console.log(`[sculpture] оболочек после среза: ${comps.length} (главная ${comps[0].tris} трис)`);
  if (comps.length > 1) {
    geometry = keepComponent(merged, roots, comps[0].root);
    console.log(`[sculpture] оставлена главная оболочка: ${geometry.index.count / 3} трис`);
  }
}

const openBefore = countBoundaryEdges(geometry);
const capping = capAtPlane(geometry, cropY);
geometry = capping.geometry;
console.log(
  `[sculpture] открытых рёбер до заглушки: ${openBefore}, ` +
    `закрыто контуров: ${capping.loops}, граней заглушки: ${capping.tris}, ` +
    `средний нормаль.y заглушки ${capping.meanNy.toFixed(3)}`
);

geometry.computeVertexNormals();

// --- ставим низ фигуры на y=0 и центрируем по X/Z -----------------------------
geometry.computeBoundingBox();
const box1 = geometry.boundingBox;
const offsetX = (box1.min.x + box1.max.x) / 2;
const offsetY = box1.min.y;
const offsetZ = (box1.min.z + box1.max.z) / 2;
const positions = geometry.attributes.position.array;
for (let i = 0; i < positions.length; i += 3) {
  positions[i] -= offsetX;
  positions[i + 1] -= offsetY;
  positions[i + 2] -= offsetZ;
}
geometry.computeBoundingBox();
geometry.computeBoundingSphere();

const box2 = geometry.boundingBox;
console.log(
  `[sculpture] итог: ${geometry.attributes.position.count} вершин, ` +
    `${geometry.index.count / 3} трис, bbox ${fmt(box2)}, ` +
    `h=${(box2.max.y - box2.min.y).toFixed(3)}, радиус ${geometry.boundingSphere.radius.toFixed(3)}`
);

if (PROFILE_ONLY) {
  console.log("[sculpture] --profile: файл не записан");
  process.exit(0);
}

const glb = buildGlb(geometry);
mkdirSync(OUT_DIR, { recursive: true });
writeFileSync(OUT, glb);
console.log(
  `[sculpture] ${OUT}  ${(glb.length / 1024 / 1024).toFixed(2)} МБ  (${Date.now() - t0} мс)`
);

// =============================================================================
function fmt(box) {
  const s = box.max.clone().sub(box.min);
  return `${s.x.toFixed(2)} x ${s.y.toFixed(2)} x ${s.z.toFixed(2)}`;
}

function positionOnly(geometry) {
  const next = new THREE.BufferGeometry();
  next.setAttribute("position", geometry.attributes.position.clone());
  return next;
}

function reportProfile(geometry, box, height, cropY, triCount, always) {
  const BINS = 24;
  const pos = geometry.attributes.position.array;
  const bins = Array.from({ length: BINS }, () => ({ n: 0, min: Infinity, max: -Infinity }));
  for (let i = 0; i < pos.length; i += 3) {
    const y = pos[i + 1];
    let k = Math.floor(((y - box.min.y) / height) * BINS);
    if (k < 0) k = 0;
    if (k >= BINS) k = BINS - 1;
    const r = Math.hypot(pos[i], pos[i + 2]);
    const bin = bins[k];
    bin.n++;
    if (r < bin.min) bin.min = r;
    if (r > bin.max) bin.max = r;
  }
  console.log(
    `[sculpture] источник ${triCount} трис, bbox ${fmt(box)}, высота ${height.toFixed(3)}`
  );
  console.log(
    `[sculpture] линия среза y=${cropY.toFixed(3)} (${(CROP_RATIO * 100).toFixed(0)}% снизу)`
  );
  if (!always) return;
  bins.forEach((b, i) => {
    const y = box.min.y + (height * (i + 0.5)) / BINS;
    console.log(
      `   bin ${String(i).padStart(2)} y=${y.toFixed(2).padStart(6)}  n=${String(b.n).padStart(6)}  r=${
        b.min === Infinity ? "-" : `${b.min.toFixed(3)}..${b.max.toFixed(3)}`
      }${y < cropY ? "  <- cut" : ""}`
    );
  });
}

/** Отсекает всё, что ниже planeY, оставляя многоугольники сечения (без индексов). */
function clipAbove(geometry, planeY) {
  const src = geometry.attributes.position.array;
  const out = [];
  let dropped = 0;
  let cut = 0;

  const emit = (a, b, c) => {
    const ux = b[0] - a[0];
    const uy = b[1] - a[1];
    const uz = b[2] - a[2];
    const vx = c[0] - a[0];
    const vy = c[1] - a[1];
    const vz = c[2] - a[2];
    const nx = uy * vz - uz * vy;
    const ny = uz * vx - ux * vz;
    const nz = ux * vy - uy * vx;
    if (nx * nx + ny * ny + nz * nz < 1e-24) return;
    out.push(a[0], a[1], a[2], b[0], b[1], b[2], c[0], c[1], c[2]);
  };

  for (let i = 0; i < src.length; i += 9) {
    const v = [
      [src[i], src[i + 1], src[i + 2]],
      [src[i + 3], src[i + 4], src[i + 5]],
      [src[i + 6], src[i + 7], src[i + 8]],
    ];
    let above = 0;
    for (const p of v) if (p[1] >= planeY) above++;

    if (above === 3) {
      emit(v[0], v[1], v[2]);
      continue;
    }
    if (above === 0) {
      dropped++;
      continue;
    }
    cut++;

    const poly = [];
    for (let k = 0; k < 3; k++) {
      const cur = v[k];
      const nxt = v[(k + 1) % 3];
      const sc = cur[1] - planeY;
      const sn = nxt[1] - planeY;
      if (sc >= 0) poly.push(cur);
      if ((sc > 0 && sn < 0) || (sc < 0 && sn > 0)) {
        const t = sc / (sc - sn);
        poly.push([
          cur[0] + (nxt[0] - cur[0]) * t,
          cur[1] + (nxt[1] - cur[1]) * t,
          cur[2] + (nxt[2] - cur[2]) * t,
        ]);
      }
    }
    for (let k = 1; k + 1 < poly.length; k++) emit(poly[0], poly[k], poly[k + 1]);
  }

  const next = new THREE.BufferGeometry();
  next.setAttribute("position", new THREE.Float32BufferAttribute(out, 3));
  return { geometry: next, tris: out.length / 9, dropped, cut };
}

/** Union-find по общим вершинам: возвращает корень для каждой вершины. */
function analyzeComponents(geometry) {
  const index = geometry.index.array;
  const vertexCount = geometry.attributes.position.count;
  const parent = new Int32Array(vertexCount);
  for (let i = 0; i < vertexCount; i++) parent[i] = i;
  const find = (a) => {
    let r = a;
    while (parent[r] !== r) r = parent[r];
    while (parent[a] !== r) {
      const next = parent[a];
      parent[a] = r;
      a = next;
    }
    return r;
  };
  const join = (a, b) => {
    const ra = find(a);
    const rb = find(b);
    if (ra !== rb) parent[Math.max(ra, rb)] = Math.min(ra, rb);
  };
  for (let i = 0; i < index.length; i += 3) {
    join(index[i], index[i + 1]);
    join(index[i + 1], index[i + 2]);
  }
  const roots = new Int32Array(vertexCount);
  const byRoot = new Map();
  for (let i = 0; i < vertexCount; i++) roots[i] = find(i);
  for (let i = 0; i < index.length; i += 3) {
    const r = roots[index[i]];
    byRoot.set(r, (byRoot.get(r) ?? 0) + 1);
  }
  return { roots, comps: [...byRoot].map(([root, tris]) => ({ root, tris })) };
}

function keepComponent(geometry, roots, root) {
  const index = geometry.index.array;
  const keep = [];
  for (let i = 0; i < index.length; i += 3) {
    if (roots[index[i]] === root) keep.push(index[i], index[i + 1], index[i + 2]);
  }
  const oldPos = geometry.attributes.position.array;
  const remap = new Map();
  const nextPos = [];
  const nextIndex = new Array(keep.length);
  for (let i = 0; i < keep.length; i++) {
    const src = keep[i];
    let dst = remap.get(src);
    if (dst === undefined) {
      dst = remap.size;
      remap.set(src, dst);
      nextPos.push(oldPos[src * 3], oldPos[src * 3 + 1], oldPos[src * 3 + 2]);
    }
    nextIndex[i] = dst;
  }
  const next = new THREE.BufferGeometry();
  next.setAttribute("position", new THREE.Float32BufferAttribute(nextPos, 3));
  next.setIndex(nextIndex);
  return next;
}

function edgeKey(a, b, vcount) {
  return a < b ? a * vcount + b : b * vcount + a;
}

/** Рёбра, принадлежащие ровно одной грани. */
function boundaryEdges(geometry) {
  const index = geometry.index.array;
  const vcount = geometry.attributes.position.count;
  const counts = new Map();
  for (let i = 0; i < index.length; i += 3) {
    for (let k = 0; k < 3; k++) {
      const a = index[i + k];
      const b = index[i + ((k + 1) % 3)];
      const key = edgeKey(a, b, vcount);
      counts.set(key, (counts.get(key) ?? 0) + 1);
    }
  }
  const out = [];
  for (let i = 0; i < index.length; i += 3) {
    for (let k = 0; k < 3; k++) {
      const a = index[i + k];
      const b = index[i + ((k + 1) % 3)];
      if (counts.get(edgeKey(a, b, vcount)) === 1) out.push([a, b]);
    }
  }
  return out;
}

function countBoundaryEdges(geometry) {
  return boundaryEdges(geometry).length;
}

/**
 * Закрывает контуры сечения на planeY плоскими гранями.
 * Вершины заглушки намеренно НЕ склеиваются с боковыми — край остаётся жёстким.
 */
function capAtPlane(geometry, planeY, eps = 1e-5) {
  const pos = geometry.attributes.position.array;
  const vcount = geometry.attributes.position.count;
  const edges = boundaryEdges(geometry).filter(([a, b]) =>
    Math.abs(pos[a * 3 + 1] - planeY) < eps && Math.abs(pos[b * 3 + 1] - planeY) < eps
  );

  const adj = new Map();
  const unused = new Set();
  const dirKey = (a, b) => a * vcount + b;
  for (const [a, b] of edges) {
    if (!adj.has(a)) adj.set(a, []);
    if (!adj.has(b)) adj.set(b, []);
    adj.get(a).push(b);
    adj.get(b).push(a);
    unused.add(dirKey(a, b));
    unused.add(dirKey(b, a));
  }

  const loops = [];
  for (const [a, b] of edges) {
    const startKey = dirKey(a, b);
    if (!unused.has(startKey)) continue;
    const loop = [a];
    let prev = a;
    let cur = b;
    unused.delete(startKey);
    unused.delete(dirKey(b, a));
    let guard = 0;
    while (cur !== a && guard++ < 100000) {
      loop.push(cur);
      const next = (adj.get(cur) ?? []).find(
        (n) => n !== prev && unused.has(dirKey(cur, n))
      );
      if (next === undefined) break;
      unused.delete(dirKey(cur, next));
      unused.delete(dirKey(next, cur));
      prev = cur;
      cur = next;
    }
    if (loop.length >= 3) loops.push(loop);
  }

  const newPos = Array.from(pos);
  const newIndex = Array.from(geometry.index.array);
  let meanNy = 0;
  let capFaces = 0;

  for (const loop of loops) {
    const poly = loop.map((v) => [pos[v * 3], pos[v * 3 + 2]]);
    if (signedArea(poly) < 0) {
      loop.reverse();
      poly.reverse();
    }
    const tris = earClip(poly);
    for (const [i0, i1, i2] of tris) {
      const base = newPos.length / 3;
      for (const idx of [loop[i0], loop[i1], loop[i2]]) {
        newPos.push(pos[idx * 3], pos[idx * 3 + 1], pos[idx * 3 + 2]);
      }
      newIndex.push(base, base + 1, base + 2);
      meanNy += faceNormalY(newPos, base);
      capFaces++;
    }
  }

  const next = new THREE.BufferGeometry();
  next.setAttribute("position", new THREE.Float32BufferAttribute(newPos, 3));
  next.setIndex(newIndex);
  return {
    geometry: next,
    loops: loops.length,
    tris: capFaces,
    meanNy: capFaces ? meanNy / capFaces : 0,
  };
}

function signedArea(poly) {
  let sum = 0;
  for (let i = 0; i < poly.length; i++) {
    const [x0, z0] = poly[i];
    const [x1, z1] = poly[(i + 1) % poly.length];
    sum += x0 * z1 - x1 * z0;
  }
  return sum / 2;
}

function faceNormalY(pos, base) {
  const ax = pos[base * 3];
  const ay = pos[base * 3 + 1];
  const az = pos[base * 3 + 2];
  const bx = pos[base * 3 + 3];
  const by = pos[base * 3 + 4];
  const bz = pos[base * 3 + 5];
  const cx = pos[base * 3 + 6];
  const cy = pos[base * 3 + 7];
  const cz = pos[base * 3 + 8];
  const ux = bx - ax;
  const uy = by - ay;
  const uz = bz - az;
  const vx = cx - ax;
  const vy = cy - ay;
  const vz = cz - az;
  const ny = uz * vx - ux * vz;
  const len = Math.hypot(uy * vz - uz * vy, ny, ux * vy - uy * vx);
  return len > 0 ? ny / len : 0;
}

/** Ранний клипинг уха для простого 2D-многоугольника (координаты [x, z], CCW). */
function earClip(poly) {
  const n = poly.length;
  const idx = Array.from({ length: n }, (_, i) => i);
  const out = [];
  let guard = 0;
  while (idx.length > 3 && guard++ < 20000) {
    let clipped = false;
    for (let i = 0; i < idx.length; i++) {
      const iPrev = idx[(i + idx.length - 1) % idx.length];
      const iCur = idx[i];
      const iNext = idx[(i + 1) % idx.length];
      const a = poly[iPrev];
      const b = poly[iCur];
      const c = poly[iNext];
      const cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
      if (cross <= 1e-18) continue;
      let inside = false;
      for (const j of idx) {
        if (j === iPrev || j === iCur || j === iNext) continue;
        if (pointInTri(poly[j], a, b, c)) {
          inside = true;
          break;
        }
      }
      if (inside) continue;
      out.push([iPrev, iCur, iNext]);
      idx.splice(i, 1);
      clipped = true;
      break;
    }
    if (!clipped) break;
  }
  if (idx.length === 3) out.push([idx[0], idx[1], idx[2]]);
  else if (idx.length > 3) {
    for (let i = 1; i + 1 < idx.length; i++) out.push([idx[0], idx[i], idx[i + 1]]);
  }
  return out;
}

function pointInTri(p, a, b, c) {
  const d1 = (p[0] - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (p[1] - b[1]);
  const d2 = (p[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (p[1] - c[1]);
  const d3 = (p[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (p[1] - a[1]);
  const neg = d1 < 0 || d2 < 0 || d3 < 0;
  const pos = d1 > 0 || d2 > 0 || d3 > 0;
  return !(neg && pos);
}

function buildGlb(geometry) {
  const positions = geometry.attributes.position.array;
  const normals = geometry.attributes.normal.array;
  const indices = geometry.index.array;

  const vertexCount = positions.length / 3;
  const useShort = vertexCount < 65536;
  const indexArray = useShort ? new Uint16Array(indices) : new Uint32Array(indices);

  const posBytes = new Uint8Array(positions.buffer, positions.byteOffset, positions.byteLength);
  const nrmBytes = new Uint8Array(normals.buffer, normals.byteOffset, normals.byteLength);
  const idxBytes = new Uint8Array(indexArray.buffer, indexArray.byteOffset, indexArray.byteLength);

  const pad4 = (n) => (n + 3) & ~3;
  const offPos = 0;
  const offNrm = pad4(offPos + posBytes.byteLength);
  const offIdx = pad4(offNrm + nrmBytes.byteLength);
  const binLength = pad4(offIdx + idxBytes.byteLength);

  const bin = new Uint8Array(binLength);
  bin.set(posBytes, offPos);
  bin.set(nrmBytes, offNrm);
  bin.set(idxBytes, offIdx);

  const box = geometry.boundingBox;
  const gltf = {
    asset: { version: "2.0", generator: "build-sculpture.mjs" },
    scene: 0,
    scenes: [{ nodes: [0] }],
    nodes: [{ mesh: 0, name: "Aphrodite" }],
    meshes: [
      {
        name: "Aphrodite",
        primitives: [{ attributes: { POSITION: 0, NORMAL: 1 }, indices: 2, material: 0 }],
      },
    ],
    materials: [
      {
        name: "Marble",
        pbrMetallicRoughness: {
          baseColorFactor: [1, 1, 1, 1],
          metallicFactor: 0,
          roughnessFactor: 0.5,
        },
        doubleSided: false,
      },
    ],
    accessors: [
      {
        bufferView: 0,
        componentType: 5126,
        count: vertexCount,
        type: "VEC3",
        min: [box.min.x, box.min.y, box.min.z],
        max: [box.max.x, box.max.y, box.max.z],
      },
      { bufferView: 1, componentType: 5126, count: vertexCount, type: "VEC3" },
      {
        bufferView: 2,
        componentType: useShort ? 5123 : 5125,
        count: indices.length,
        type: "SCALAR",
      },
    ],
    bufferViews: [
      { buffer: 0, byteOffset: offPos, byteLength: posBytes.byteLength, target: 34962 },
      { buffer: 0, byteOffset: offNrm, byteLength: nrmBytes.byteLength, target: 34962 },
      { buffer: 0, byteOffset: offIdx, byteLength: idxBytes.byteLength, target: 34963 },
    ],
    buffers: [{ byteLength: binLength }],
  };

  const encoder = new TextEncoder();
  let json = encoder.encode(JSON.stringify(gltf));
  const jsonPad = (4 - (json.byteLength % 4)) % 4;
  if (jsonPad) {
    const padded = new Uint8Array(json.byteLength + jsonPad);
    padded.fill(0x20);
    padded.set(json);
    json = padded;
  }

  const total = 12 + 8 + json.byteLength + 8 + bin.byteLength;
  const out = new Uint8Array(total);
  const view = new DataView(out.buffer);

  view.setUint32(0, 0x46546c67, true);
  view.setUint32(4, 2, true);
  view.setUint32(8, total, true);

  view.setUint32(12, json.byteLength, true);
  view.setUint32(16, 0x4e4f534a, true);
  out.set(json, 20);

  const binHeader = 20 + json.byteLength;
  view.setUint32(binHeader, bin.byteLength, true);
  view.setUint32(binHeader + 4, 0x004e4942, true);
  out.set(bin, binHeader + 8);

  return out;
}
