# Пластический хирург — интерактивный 3D-лендинг

**Live:** [mary-rnd.github.io/vebinar-ii-analitik-landing](https://mary-rnd.github.io/vebinar-ii-analitik-landing/)

Промо-лендинг практики пластической хирургии: тёмный кинематографичный дизайн, интерактивная 3D-скульптура в герое и постраничный сторителлинг от «роли хирурга» до записи на первую консультацию.

---

## Скриншоты

### Герой — интерактивная 3D-сцена

![Герой — 3D-сцена с фигурами](screenshots/hero-desktop.png)

### Страница «Послеродовое восстановление»

![Послеродовое восстановление — 3D-фигура с зонами коррекции](screenshots/subpage-postpartum.png)

### Обзор всей главной страницы

![Полная главная страница](screenshots/fullpage-desktop.png)

### Мобильная версия

![Мобильная версия](screenshots/mobile.png)

---

## Что внутри

- **3D-герой на React Three Fiber** — две скульптуры, hover-зоны по частям тела с подсказками направлений, по скроллу фигуры расходятся к краям экрана (sticky-сцена высотой 200vh).
- **3D-блок «Послеродовое восстановление»** — отдельная зона `ZoneFigure`: наводишь на живот/грудь/бёдра — видишь, какое вмешательство обсуждают на консультации; клик ведёт на страницу маршрута.
- **Анимации** — stagger-reveal заголовков, scroll-progress bar, карточки с подъёмом при наведении, shine-эффект на кнопках, бесконечная marquee-лента направлений, параллакс.
- **Секции** — философия подхода, направления (BodyMaps), маршрут восстановления, о хирурге (фото-карточка), как проходит консультация, FAQ-аккордеон, форма заявки.
- **Форма заявки** — интеграция с Web3Forms: заявки уходят на почту без бэкенда (важно для статического хостинга).
- **Политика конфиденциальности** и согласие на обработку данных — отдельная страница `/policy`.
- **SEO-метаданные** — title, description, Open Graph, Twitter Card, favicon.

## Стек

| Слой | Технологии |
| --- | --- |
| Фреймворк | Next.js 16 (App Router), React, TypeScript |
| Стили | Tailwind v4, кастомная палитра (marble / ink / gold / bronze) |
| 3D | three.js, React Three Fiber, drei |
| Анимации | GSAP, CSS-transitions, IntersectionObserver |
| Шрифты | Cormorant Garamond (display) + Manrope (sans) |
| Формы | Web3Forms (serverless, без API-роутов) |
| Хостинг | GitHub Pages, статический экспорт + GitHub Actions |

## Локальный запуск

```bash
cd "Surgery landing/site"
npm install --legacy-peer-deps
npm run dev        # http://localhost:3000
```

```bash
npm run build      # статический экспорт в out/ (+ postbuild-фикс RSC-алиасов)
```

## Деплой

Пуш в ветку `main` с изменениями в `Surgery landing/site/**` запускает GitHub Actions
(`.github/workflows/deploy-surgery-pages.yml`): сборка с `NEXT_PUBLIC_BASE_PATH` → публикация
`out/` через `actions/deploy-pages`. Сайт живёт по адресу
`https://mary-rnd.github.io/vebinar-ii-analitik-landing/`.

## Структура

```
Surgery landing/
├── README.md               ← этот файл
├── screenshots/            ← скриншоты для портфолио
└── site/
    ├── src/app/            # маршруты: /, /policy, /muzhskaya-plastika, /poslerodovoe-vosstanovlenie
    ├── src/components/     # UI-секции (Header, FAQ, ContactForm, …)
    ├── src/components/three/  # HeroSection, ZoneFigure, фигуры и сцены
    ├── public/             # фото, текстуры
    ├── scripts/            # postbuild-фикс экспортa
    └── out/                # собранный статический сайт (не в git)
```

---

Фото хирурга: [Pexels](https://www.pexels.com/photo/6303569) (свободная лицензия).
