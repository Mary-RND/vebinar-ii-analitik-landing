import { readdir, readFile, writeFile, mkdir, copyFile } from "node:fs/promises";
import { join } from "node:path";

const root = process.argv[2] || "out";
let created = 0;

async function walk(dir) {
  let entries;
  try {
    entries = await readdir(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    const path = join(dir, entry.name);
    if (!entry.isDirectory()) continue;
    if (entry.name.startsWith("__next.")) {
      const files = await readdir(path, { withFileTypes: true });
      for (const file of files) {
        if (!file.isFile()) continue;
        const source = join(path, file.name);
        const alias = join(dir, `${entry.name}.${file.name}`);
        await writeFile(alias, await readFile(source));
        created++;
      }
    } else {
      await walk(path);
    }
  }
}

await walk(root);

// Trailing-slash URLs: GH Pages serves `X/index.html` for `X/`, but export only
// writes root-level `X.html`. Mirror html/txt into `X/index.*`.
const entries = await readdir(root, { withFileTypes: true });
let dirs = 0;
for (const entry of entries) {
  if (!entry.isFile()) continue;
  if (!entry.name.endsWith(".html") && !entry.name.endsWith(".txt")) continue;
  const ext = entry.name.endsWith(".html") ? "html" : "txt";
  const route = entry.name.replace(/\.(html|txt)$/, "");
  if (route === "index" || route === "404") continue;
  if (!entries.some((e) => e.isDirectory() && e.name === route)) continue;
  await copyFile(join(root, entry.name), join(root, route, `index.${ext}`));
  dirs++;
}

console.log(`RSC payload aliases created: ${created}, route index mirrors: ${dirs}`);