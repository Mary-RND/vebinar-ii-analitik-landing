import { readdir, readFile, writeFile } from "node:fs/promises";
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
console.log(`RSC payload aliases created: ${created}`);