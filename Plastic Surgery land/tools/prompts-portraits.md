# Промпты для портретов (AI Studio / любая image-модель)

Используются в `tools/gen-images.mjs` при генерации через Replicate.
Совпадают 1 в 1 — чтобы результат можно было повторить любым способом.

**Общая стилистика (подставляется в конец каждого промпта):**

```
premium clinical editorial portrait photography for a modern plastic surgery practice,
cool clean palette of white, soft fog grey and misty pale blue with subtle indigo accents,
soft diffused north-facing window light, gentle film grain, shallow depth of field,
calm minimal composition, high-end medical brand aesthetic,
photorealistic, no text, no watermark, no logo, no letters
```

**Рекомендуемое соотношение сторон:** 4:5 (портрет). Имя файла — вторая строка.

---

## 1. `surgeon.jpg`

```
Editorial portrait of a calm experienced male plastic surgeon in his early 40s,
short dark hair with a touch of grey at the temples, clean-shaven, wearing a crisp
white medical coat over a light blue shirt, standing in a bright minimal clinic corridor
with pale grey walls, confident restrained expression, arms relaxed, three-quarter view,
trustworthy expert mood, [СТИЛЬ]
```

## 2. `team-anesthesiologist.jpg`

```
Editorial portrait of a professional female anesthesiologist-reanimatologist in her
late 30s, dark hair pulled back neatly, subtle makeup, wearing a white medical coat
with a stethoscope around her neck, standing against a soft pale blue clinic wall,
composed attentive expression, calm reassuring mood, vertical portrait, [СТИЛЬ]
```

## 3. `team-assistant.jpg`

```
Editorial portrait of a focused male surgical assistant in his early 30s, short light
brown hair, neat appearance, wearing light blue surgical scrubs, standing in a clean
modern operating room with soft white lighting, arms crossed, precise professional mood,
vertical portrait, [СТИЛЬ]
```

## 4. `team-nurse.jpg`

```
Editorial portrait of a warm professional operating room nurse in her early 30s,
blonde hair in a neat bun, wearing light blue surgical scrubs and a cap, standing beside
stainless steel instrument trolley in a bright sterile operating room, gentle confident
smile, meticulous mood, vertical portrait, [СТИЛЬ]
```

## 5. `team-coordinator.jpg`

```
Editorial portrait of a friendly female patient coordinator in her late 20s,
shoulder-length brown hair, wearing a soft cream blazer over a pale blue top, holding
a slim tablet, standing in a minimal light grey clinic reception with soft daylight,
warm approachable smile, welcoming mood, vertical portrait, [СТИЛЬ]
```

---

## Куда класть результат

```
C:\Users\User\Documents\Freelance\Plastic Surgery land\assets\images\
```

Имена файлов строго как указано — сайт будет ссылаться на них.

## Если пойдём через Replicate (вместо AI Studio)

```
node "C:\Users\User\Documents\Freelance\Plastic Surgery land\tools\gen-images.mjs"
```

Одна картинка: `node ... gen-images.mjs surgeon.jpg`
Нужен `REPLICATE_API_TOKEN` (лежит в `C:\Users\User\.config\opencode\secrets\replicate.env`)
и баланс на аккаунте `mary-rnd` — сейчас **0**, HTTP 402.
