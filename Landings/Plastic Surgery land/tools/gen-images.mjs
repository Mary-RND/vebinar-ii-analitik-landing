import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const OUT_DIR = path.join(ROOT, "assets", "images");
const ENV_FILE = "C:\\Users\\User\\.config\\opencode\\secrets\\cloudflare.env";

const MODEL = "@cf/black-forest-labs/flux-1-schnell";

const STYLE = `premium clinical editorial portrait photography for a modern plastic surgery practice,
cool clean palette of white, soft fog grey and misty pale blue with subtle indigo accents,
soft diffused north-facing window light, gentle film grain, shallow depth of field,
calm minimal composition, high-end medical brand aesthetic,
photorealistic, no text, no watermark, no logo, no letters`;

const JOBS = [
  {
    file: "surgeon.jpg",
    seed: 2101,
    prompt: `Editorial portrait of a calm experienced male plastic surgeon in his early 40s,
short dark hair with a touch of grey at the temples, clean-shaven, wearing a crisp
white medical coat over a light blue shirt, standing in a bright minimal clinic corridor
with pale grey walls, confident restrained expression, arms relaxed, three-quarter view,
trustworthy expert mood`,
  },
  {
    file: "team-anesthesiologist.jpg",
    seed: 2102,
    prompt: `Editorial portrait of a professional female anesthesiologist-reanimatologist in her
late 30s, dark hair pulled back neatly, subtle makeup, wearing a white medical coat
with a stethoscope around her neck, standing against a soft pale blue clinic wall,
composed attentive expression, calm reassuring mood, vertical portrait`,
  },
  {
    file: "team-assistant.jpg",
    seed: 2103,
    prompt: `Editorial portrait of a focused male surgical assistant in his early 30s, short light
brown hair, neat appearance, wearing light blue surgical scrubs, standing in a clean
modern operating room with soft white lighting, arms crossed, precise professional mood,
vertical portrait`,
  },
  {
    file: "team-nurse.jpg",
    seed: 2104,
    prompt: `Editorial portrait of a warm professional operating room nurse in her early 30s,
blonde hair in a neat bun, wearing light blue surgical scrubs and a cap, standing beside
stainless steel instrument trolley in a bright sterile operating room, gentle confident
smile, meticulous mood, vertical portrait`,
  },
  {
    file: "team-coordinator.jpg",
    seed: 2105,
    prompt: `Editorial portrait of a friendly female patient coordinator in her late 20s,
shoulder-length brown hair, wearing a soft cream blazer over a pale blue top, holding
a slim tablet, standing in a minimal light grey clinic reception with soft daylight,
warm approachable smile, welcoming mood, vertical portrait`,
  },
];

function loadEnv() {
  const out = {};
  const merge = (text) => {
    for (const line of text.split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
      if (m) out[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
  };
  if (process.env.CF_ACCOUNT_ID) out.CF_ACCOUNT_ID = process.env.CF_ACCOUNT_ID;
  if (process.env.CF_API_TOKEN) out.CF_API_TOKEN = process.env.CF_API_TOKEN;
  if (fs.existsSync(ENV_FILE)) merge(fs.readFileSync(ENV_FILE, "utf8"));
  return out;
}

const env = loadEnv();
const ACCOUNT = env.CF_ACCOUNT_ID;
const TOKEN = env.CF_API_TOKEN;

if (!ACCOUNT || !TOKEN) {
  console.error("Нет CF_ACCOUNT_ID / CF_API_TOKEN (env или " + ENV_FILE + ")");
  process.exit(1);
}

// Модель отдаёт только 1024x1024: width/height/steps/seed схема не принимает.
const PAUSE_MS = 3000;

async function generate(job) {
  const url = `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT}/ai/run/${MODEL}`;
  const body = {
    prompt: `${job.prompt.trim()}, ${STYLE}`,
  };

  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const ctype = res.headers.get("content-type") || "";
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status} ${ctype}: ${text.slice(0, 400)}`);
  }

  let buffer;
  if (ctype.startsWith("image/")) {
    buffer = Buffer.from(await res.arrayBuffer());
  } else {
    const json = await res.json();
    const r = json.result ?? json;
    if (r.image) {
      buffer = Buffer.from(r.image, "base64");
    } else if (r.image_url) {
      const dl = await fetch(r.image_url);
      buffer = Buffer.from(await dl.arrayBuffer());
    } else if (json.errors?.length) {
      throw new Error("API errors: " + JSON.stringify(json.errors).slice(0, 400));
    } else {
      throw new Error("Неизвестный ответ: " + JSON.stringify(json).slice(0, 400));
    }
  }

  if (buffer.length < 5000) {
    throw new Error("Слишком маленький ответ: " + buffer.length + " байт");
  }
  return buffer;
}

async function main() {
  const only = process.argv[2];
  const jobs = only ? JOBS.filter((j) => j.file === only) : JOBS;
  if (!jobs.length) {
    console.error("Нет задачи с именем " + only);
    process.exit(1);
  }
  fs.mkdirSync(OUT_DIR, { recursive: true });

  let ok = 0;
  let fail = 0;
  for (const job of jobs) {
    const dest = path.join(OUT_DIR, job.file);
    const started = Date.now();
    try {
      const buf = await generate(job);
      fs.writeFileSync(dest, buf);
      const kb = Math.round(buf.length / 1024);
      console.log(`OK   ${job.file}  ${kb} КБ  ${((Date.now() - started) / 1000).toFixed(1)}с`);
      ok++;
    } catch (err) {
      console.error(`FAIL ${job.file}: ${err.message}`);
      fail++;
    }
    if (jobs.length > 1) await new Promise((r) => setTimeout(r, PAUSE_MS));
  }

  console.log(`\nГотово: ${ok} из ${jobs.length}, ошибок: ${fail}`);
  process.exit(fail ? 1 : 0);
}

main();
