import fs from "node:fs";

const path = process.argv[2];
const buf = fs.readFileSync(path);

function parseGLB(b) {
  const dv = new DataView(b.buffer, b.byteOffset, b.byteLength);
  if (dv.getUint32(0, true) !== 0x46546c67) throw new Error("not glb");
  let off = 12;
  let json = null;
  let bin = null;
  while (off < b.byteLength) {
    const len = dv.getUint32(off, true);
    const type = dv.getUint32(off + 4, true);
    const data = b.subarray(off + 8, off + 8 + len);
    if (type === 0x4e4f534a) json = JSON.parse(data.toString("utf8"));
    else if (type === 0x004e4942) bin = data;
    off += 8 + len + ((4 - (len % 4)) % 4) * 0;
  }
  return { json, bin };
}

const { json, bin } = parseGLB(buf);
const mesh = json.meshes[0];
const prim = mesh.primitives[0];

function readAccessor(idx) {
  const acc = json.accessors[idx];
  const bv = json.bufferViews[acc.bufferView];
  const comp = { 5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4 }[acc.componentType];
  const num = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4 }[acc.type];
  const comps = comp * num;
  const stride = bv.byteStride || comps;
  const base = (bv.byteOffset || 0) + (acc.byteOffset || 0);
  const out = [];
  for (let i = 0; i < acc.count; i++) {
    const o = base + i * stride;
    if (acc.componentType === 5126) {
      const v = [];
      for (let c = 0; c < num; c++) v.push(new DataView(bin.buffer, bin.byteOffset + o + c * 4, 4).getFloat32(0, true));
      out.push(num === 1 ? v[0] : v);
    } else if (acc.componentType === 5125) {
      out.push(new DataView(bin.buffer, bin.byteOffset + o, 4).getUint32(0, true));
    } else if (acc.componentType === 5123) {
      out.push(new DataView(bin.buffer, bin.byteOffset + o, 2).getUint16(0, true));
    }
  }
  return out;
}

const pos = readAccessor(prim.attributes.POSITION);
const idx = readAccessor(prim.indices);
console.log("positions:", pos.length, "indices:", idx.length, "tris:", idx.length / 3);

const bbox = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity];
for (const p of pos) {
  for (let i = 0; i < 3; i++) {
    if (p[i] < bbox[i]) bbox[i] = p[i];
    if (p[i] > bbox[i + 3]) bbox[i + 3] = p[i];
  }
}
console.log("bbox:", bbox.map((v) => v.toFixed(3)).join(" .. "));

const edges = new Map(); // key a<b -> {count, sameDir}
for (let t = 0; t < idx.length; t += 3) {
  const a = idx[t], b = idx[t + 1], c = idx[t + 2];
  for (const [u, v] of [[a, b], [b, c], [c, a]]) {
    const k = u < v ? u * 1e7 + v : v * 1e7 + u;
    const e = edges.get(k);
    if (!e) edges.set(k, { a: u < v ? u : v, b: u < v ? v : u, count: 1, fwd: u < v ? 1 : 0 });
    else { e.count++; if (u < v) e.fwd++; }
  }
}
let boundary = 0, nonmanifold = 0, winding = 0;
const boundaryEdges = [];
for (const e of edges.values()) {
  if (e.count === 1) { boundary++; boundaryEdges.push(e); }
  else if (e.count > 2) nonmanifold++;
  else if (e.fwd === 2 || e.fwd === 0) winding++;
}
console.log("edges:", edges.size, "boundary(1):", boundary, "nonmanifold(>2):", nonmanifold, "same-direction pairs:", winding);

// boundary loops: chain boundary edges
const adj = new Map();
for (const e of boundaryEdges) {
  if (!adj.has(e.a)) adj.set(e.a, []);
  if (!adj.has(e.b)) adj.set(e.b, []);
  adj.get(e.a).push(e.b);
  adj.get(e.b).push(e.a);
}
const seen = new Set();
const loops = [];
for (const start of adj.keys()) {
  if (seen.has(start)) continue;
  const stack = [start];
  const comp = [];
  seen.add(start);
  while (stack.length) {
    const n = stack.pop();
    comp.push(n);
    for (const m of adj.get(n)) if (!seen.has(m)) { seen.add(m); stack.push(m); }
  }
  const ys = comp.map((i) => pos[i][1]);
  const xs = comp.map((i) => pos[i][0]);
  const zs = comp.map((i) => pos[i][2]);
  loops.push({
    verts: comp.length,
    y: [Math.min(...ys), Math.max(...ys)],
    x: [Math.min(...xs), Math.max(...xs)],
    z: [Math.min(...zs), Math.max(...zs)],
  });
}
loops.sort((p, q) => q.verts - p.verts);
console.log("boundary loops:", loops.length);
const offPlane = loops.filter((l) => l.y[1] > 0.005);
console.log("loops NOT at cut plane (y>0.005):", offPlane.length, "total verts:", offPlane.reduce((s, l) => s + l.verts, 0));
for (const l of offPlane.slice(0, 40)) {
  console.log(
    `  n=${l.verts} y=[${l.y[0].toFixed(3)},${l.y[1].toFixed(3)}] x=[${l.x[0].toFixed(3)},${l.x[1].toFixed(3)}] z=[${l.z[0].toFixed(3)},${l.z[1].toFixed(3)}]`
  );
}
const bands = {};
for (const l of offPlane) {
  const b = Math.floor(l.y[0] * 10) / 10;
  bands[b] = (bands[b] || 0) + l.verts;
}
console.log("off-plane boundary verts by y-band:", bands);

for (const e of edges.values()) {
  if (e.count > 2) {
    const a = pos[e.a], b = pos[e.b];
    console.log(`  nonmanifold edge n=${e.count} y=[${a[1].toFixed(3)},${b[1].toFixed(3)}] x=[${a[0].toFixed(3)},${b[0].toFixed(3)}]`);
  }
}
