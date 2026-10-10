# -*- coding: utf-8 -*-
"""Инвестиционная презентация VitaGen-AI — синяя гамма, 16:9."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# палитра (синяя медицинская)
DEEP = RGBColor(0x0A, 0x2F, 0x4F)     # глубокий тёмно-синий
MID = RGBColor(0x14, 0x5D, 0xA0)      # средний синий
BRIGHT = RGBColor(0x2E, 0x9E, 0xD8)   # яркий синий (акцент)
SKY = RGBColor(0xD6, 0xEA, 0xF7)      # светло-голубой фон
ICE = RGBColor(0xF2, 0xF8, 0xFC)      # почти белый синеватый
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x1A, 0x2A, 0x3A)     # текст
GRAY = RGBColor(0x5A, 0x6A, 0x7A)
GOLD = RGBColor(0xE8, 0xA7, 0x3C)     # редкий акцент (для ключевых цифр)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

W = prs.slide_width
H = prs.slide_height


def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    s.shadow.inherit = False
    return s


def tb(slide, x, y, w, h, text, size=18, bold=False, color=DARK,
       align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font="Segoe UI", line_spacing=1.0):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = ln
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = font
    return box


def bullets(slide, x, y, w, h, items, size=16, color=DARK, spacing=1.15, bold_head=False):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(8)
        p.line_spacing = spacing
        if isinstance(it, tuple):
            head, rest = it
            r0 = p.add_run(); r0.text = "▪  " + head
            r0.font.size = Pt(size); r0.font.bold = True; r0.font.color.rgb = MID; r0.font.name = "Segoe UI"
            r1 = p.add_run(); r1.text = rest
            r1.font.size = Pt(size); r1.font.color.rgb = color; r1.font.name = "Segoe UI"
        else:
            r = p.add_run(); r.text = "▪  " + it
            r.font.size = Pt(size); r.font.color.rgb = color; r.font.name = "Segoe UI"
            r.font.bold = bold_head
    return box


def slide_chrome(idx, title, subtitle=None):
    """Стандартная страница: верхняя синяя полоса, заголовок, подвал, номер."""
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, W, Inches(1.15), DEEP)
    rect(s, 0, Inches(1.15), W, Pt(4), BRIGHT)
    tb(s, Inches(0.55), Inches(0.22), Inches(11.6), Inches(0.75), title,
       size=28, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    if subtitle:
        tb(s, Inches(0.55), Inches(1.35), Inches(12.2), Inches(0.4), subtitle,
           size=14, color=GRAY, font="Segoe UI")
    # подвал
    rect(s, 0, H - Inches(0.38), W, Inches(0.38), ICE)
    tb(s, Inches(0.55), H - Inches(0.33), Inches(8), Inches(0.3),
       "VitaGen-AI  ·  Коммерческая тайна  ·  2026", size=10, color=GRAY)
    tb(s, W - Inches(1.3), H - Inches(0.33), Inches(0.9), Inches(0.3),
       f"{idx} / 13", size=10, color=GRAY, align=PP_ALIGN.RIGHT)
    return s


def kpi_card(slide, x, y, w, h, value, label, val_color=MID):
    rect(slide, x, y, w, h, ICE, line=SKY)
    rect(slide, x, y, Pt(5), h, BRIGHT)
    tb(slide, x + Inches(0.18), y + Inches(0.12), w - Inches(0.3), Inches(0.55),
       value, size=26, bold=True, color=val_color)
    tb(slide, x + Inches(0.18), y + h - Inches(0.55), w - Inches(0.3), Inches(0.45),
       label, size=11.5, color=GRAY)


def styled_table(slide, x, y, w, h, headers, rows, col_ws=None, hdr_size=12, body_size=11):
    t = slide.shapes.add_table(len(rows) + 1, len(headers), x, y, w, h).table
    if col_ws:
        total = sum(col_ws)
        for j, cw in enumerate(col_ws):
            t.columns[j].width = Emu(int(w * cw / total))
    for j, htxt in enumerate(headers):
        c = t.cell(0, j)
        c.text = ""
        c.fill.solid(); c.fill.fore_color.rgb = MID
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = htxt
        r.font.size = Pt(hdr_size); r.font.bold = True; r.font.color.rgb = WHITE
        r.font.name = "Segoe UI"
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i + 1, j)
            c.text = ""
            c.fill.solid()
            c.fill.fore_color.rgb = WHITE if i % 2 == 0 else ICE
            p = c.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            r = p.add_run(); r.text = str(val)
            r.font.size = Pt(body_size); r.font.color.rgb = DARK
            r.font.name = "Segoe UI"
            if j > 0:
                c.text_frame.word_wrap = True
    return t


# ==================== 1. ОБЛОЖКА ====================
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, W, H, DEEP)
rect(s, 0, Inches(5.9), W, Inches(1.6), MID)
# декоративные полосы
rect(s, 0, Inches(5.75), W, Pt(5), BRIGHT)
tb(s, Inches(0.9), Inches(1.15), Inches(11.5), Inches(1.0),
   "VitaGen-AI", size=54, bold=True, color=WHITE)
tb(s, Inches(0.9), Inches(2.15), Inches(11.2), Inches(1.6),
   "Мультимодальная платформа прогнозирования\nрепродуктивных исходов ВРТ на основе ИИ",
   size=28, color=BRIGHT, line_spacing=1.25)
tb(s, Inches(0.9), Inches(4.05), Inches(11.2), Inches(0.9),
   "Инвестиционное предложение · Seed 35 млн ₽ + Series A 45 млн ₽\nФедеральный рынок России · Международное направление: Хайнань (КНР) и АТР",
   size=16, color=SKY, line_spacing=1.3)
tb(s, Inches(0.9), Inches(6.2), Inches(8), Inches(1.0),
   "Петрушина М. В. · генеральный директор\nООО «МедТехПрима» · +7 985 728 66 55 · mar.petrushina@yandex.ru",
   size=14, color=WHITE, line_spacing=1.3)
tb(s, W - Inches(3.3), Inches(6.35), Inches(2.6), Inches(0.7),
   "Октябрь 2026\nСтадия: прототип + валидация",
   size=13, color=SKY, align=PP_ALIGN.RIGHT, line_spacing=1.2)

# ==================== 2. ПРОБЛЕМА ====================
s = slide_chrome(2, "Проблема: эффективность ВРТ ограничена качеством данных",
                 "Субъективная оценка эмбриолога, скрытые факторы мужского и иммунного риска, растущая нагрузка на ОМС")
kpi_card(s, Inches(0.55), Inches(1.95), Inches(2.9), Inches(1.5), "≈120–130 тыс.", "циклов ВРТ в год в РФ (ФР ВРТ МЗ РФ)")
kpi_card(s, Inches(3.65), Inches(1.95), Inches(2.9), Inches(1.5), "≈35–40%", "средняя реализация на перенос (МЗ РФ)")
kpi_card(s, Inches(6.75), Inches(1.95), Inches(2.9), Inches(1.5), "15–17%", "пар в мире сталкиваются с бесплодием (ВОЗ)")
kpi_card(s, Inches(9.85), Inches(1.95), Inches(2.9), Inches(1.5), "≈1,4", "СКР в РФ — ниже уровня воспроизводства (Росстат)")
bullets(s, Inches(0.55), Inches(3.8), Inches(12.2), Inches(3.0), [
    ("Скрытые потери: ", "до 50% неудач переносов объясняются генетикой эмбриона, качеством эндометрия, иммунной несовместимостью и мужским фактором — в клинической практике они частично «невидимы»."),
    ("Мужской фактор недооценён: ", "DFI/MAR-тест часто не включён в протокол решения о переносе — источник ранних потерь и неудачных циклов."),
    ("ОМС и бюджеты: ", "каждый повторный цикл — прямые затраты квот; регионам нужен инструмент управления CLBR и стоимостью живорождения."),
    ("Регуляторный тренд: ", "Минздрав и ДЗМ инициируют режимы упрощённой валидации («песочница») для ИИ-МИ — окно для суверенных российских решений."),
])

# ==================== 3. РЕШЕНИЕ ====================
s = slide_chrome(3, "Решение: 5 уровней данных → единый прогноз имплантации",
                 "ИИ-модель объединяет эмбрионику, геномику, клинику и мужской фактор в воспроизводимый цифровой скор")
levels = [
    ("1", "Морфокинетика", "Таймлапс, 20 000+ кадров,\n37 параметров развития"),
    ("2", "Геном эмбриона", "PGT-A, маркеры\nимплантационного потенциала"),
    ("3", "Клиника пациентки", "Возраст, АМГ, ИМТ, история ВРТ,\nэндометрий, гормоны"),
    ("4", "Геном пациентки", "PRS репродуктивного здоровья,\nKIR/HLA-C, иммунный риск"),
    ("5", "Мужской фактор", "DFI, MAR-тест, спермограмма,\nИКСИ/ПИКСИ"),
]
for i, (num, title, desc) in enumerate(levels):
    x = Inches(0.55 + i * 2.5)
    rect(s, x, Inches(1.95), Inches(2.32), Inches(2.5), ICE, line=SKY)
    circ = rect(s, x + Inches(0.85), Inches(2.1), Inches(0.6), Inches(0.6), MID, shape=MSO_SHAPE.OVAL)
    tb(s, x + Inches(0.85), Inches(2.18), Inches(0.6), Inches(0.5),
       num, size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tb(s, x + Inches(0.12), Inches(2.85), Inches(2.08), Inches(0.5),
       title, size=14, bold=True, color=DEEP, align=PP_ALIGN.CENTER)
    tb(s, x + Inches(0.12), Inches(3.35), Inches(2.08), Inches(0.95),
       desc, size=11, color=GRAY, align=PP_ALIGN.CENTER, line_spacing=1.1)
rect(s, Inches(0.55), Inches(4.75), Inches(12.25), Inches(1.9), DEEP)
tb(s, Inches(0.9), Inches(4.95), Inches(11.5), Inches(1.6),
   "Прогноз имплантационного потенциала 0–100 + рекомендация селективного переноса\n"
   "Архитектура с masking: работает при неполных данных (донорские циклы, ограниченный генотип)\n"
   "Предварительная внутренняя валидация: AUC = 0,89 (требуется проспективное исследование)",
   size=15, color=WHITE, line_spacing=1.35)

# ==================== 4. ПРОДУКТ / МОДУЛИ ====================
s = slide_chrome(4, "Продукт: платформа на весь путь пациента в ВРТ",
                 "Ядро + модульная линейка: от стимуляции до перинатальных прогнозов и матчинга донорства")
mods = [
    ("Ядро 2026–27", "Прогноз имплантации,\nселективный перенос", MID),
    ("niPGT-A 2028", "Неинвазивный прогноз\nплоидности", BRIGHT),
    ("СГЯ 2028", "Ответ яичников,\nбезопасная доза", BRIGHT),
    ("Эндометрий 2028", "Рецептивность,\nоптимизация дня переноса", BRIGHT),
    ("CLBR / CPLB 2028", "B2G: эффективность\nклиники и региона", MID),
    ("Матчинг СМ 2029", "KIR/HLA-C: доноры\nи суррогатные матери", MID),
    ("Семейный геном\n2029–30", "Pre-PGT-M/SR, AZF,\nPRS отца, эпигенетика", DEEP),
    ("Перинатальный\n2030", "Риски ранних потерь,\nпрэклампсия, ЗРП", DEEP),
]
for i, (title, desc, col) in enumerate(mods):
    row, col_i = divmod(i, 4)
    x = Inches(0.55 + col_i * 3.15)
    y = Inches(1.9 + row * 1.75)
    rect(s, x, y, Inches(2.95), Inches(1.55), ICE, line=SKY)
    rect(s, x, y, Inches(2.95), Pt(5), col)
    tb(s, x + Inches(0.15), y + Inches(0.15), Inches(2.65), Inches(0.62),
       title, size=13.5, bold=True, color=col, line_spacing=1.0)
    tb(s, x + Inches(0.15), y + Inches(0.8), Inches(2.65), Inches(0.65),
       desc, size=11.5, color=GRAY, line_spacing=1.1)
tb(s, Inches(0.55), Inches(5.55), Inches(12.2), Inches(1.3),
   "Клинические сценарии: донорские ооциты + сперма отца · ооциты матери + донорская сперма ·\n"
   "суррогатное материнство (patient_id_gestational, иммунный консилиум «СМ vs отец»).",
   size=14, color=DARK, line_spacing=1.3)
tb(s, Inches(0.55), Inches(6.55), Inches(12.2), Inches(0.5),
   "Этические границы: PGT-P по немедицинским признакам не применяется.",
   size=12, color=GRAY)

# ==================== 5. РЫНОК ====================
s = slide_chrome(5, "Рынок: Россия — федеральный запуск, АТР — масштаб",
                 "Оценки с атрибуцией: ФР ВРТ МЗ РФ, Росстат, ВОЗ; часть величин — экспертные оценки")
# воронка TAM/SAM/SOM
funnel = [
    ("TAM", "25–30 млрд ₽/год", "клинический рынок ВРТ РФ\n(~125 тыс. циклов × ~200 тыс. ₽)", DEEP),
    ("SAM", "2–3 млрд ₽/год", "софт и аналитика\nдля клиник ВРТ", MID),
    ("SOM 2030", "391 млн ₽/год", "85 клиник, 5 регионов B2G,\nранний вход в Китай", BRIGHT),
]
for i, (tag, val, desc, col) in enumerate(funnel):
    x = Inches(0.55 + i * 4.25)
    rect(s, x, Inches(1.95), Inches(3.9), Inches(2.35), ICE, line=SKY)
    rect(s, x, Inches(1.95), Inches(3.9), Inches(0.5), col)
    tb(s, x + Inches(0.15), Inches(2.02), Inches(3.6), Inches(0.4),
       tag, size=15, bold=True, color=WHITE)
    tb(s, x + Inches(0.15), Inches(2.6), Inches(3.6), Inches(0.55),
       val, size=24, bold=True, color=col)
    tb(s, x + Inches(0.15), Inches(3.25), Inches(3.6), Inches(0.9),
       desc, size=12.5, color=GRAY, line_spacing=1.2)
bullets(s, Inches(0.55), Inches(4.6), Inches(6.0), Inches(2.4), [
    ("Китай: ", "~700–800 тыс. циклов/год, клиника ~$15–20 млрд, рост ~10–15%/год (отраслевые оценки)."),
    ("Вход через Хайнань: ", "WFOE в ЗСТ, льготный КН 15%, пилот Боао Лэчэн, NMPA II класс 12–18 мес."),
    ("Данные (PIPL): ", "геномные данные не покидают КНР — локальный деплой."),
], size=14)
bullets(s, Inches(6.85), Inches(4.6), Inches(5.9), Inches(2.4), [
    ("Драйвер РФ: ", "приказ Минздрава об ИИ в ВРТ → проникновение как у таймлапса."),
    ("B2G: ", "ДЗМ Москвы — пилотный регион; CLBR и стоимость живорождения."),
    ("APAC-пайплайн: ", "Индия, Япония, Корея, Сингапур, Индонезия."),
], size=14)

# ==================== 6. БИЗНЕС-МОДЕЛЬ ====================
s = slide_chrome(6, "Бизнес-модель: B2B + B2G + APAC, asset-light",
                 "5 источников выручки · горизонт LTV клиники 5 лет · LTV/CAC > 10")
streams = [
    ("Подписка клиники", "2,2–2,8 млн ₽/год", "SaaS + базовая аналитика\n(включены обновления)"),
    ("Модули (ARPU)", "0,15–1,0 млн ₽/год", "niPGT-A, эндометрий,\nмужской геном и др."),
    ("Матчинг СМ", "0,18 млн ₽ / случай", "донорство и суррогатия —\nвысокий чек"),
    ("B2G-аналитика", "4–6 млн ₽/год", "CLBR / Cost per Live Birth,\nрегион и клиника"),
    ("APAC-лицензия", "8–8,5 млн ₽/год", "партнёр Хайнань/АТР,\nrev-share"),
]
for i, (title, price, desc) in enumerate(streams):
    x = Inches(0.55 + i * 2.5)
    rect(s, x, Inches(1.95), Inches(2.32), Inches(2.9), ICE, line=SKY)
    rect(s, x, Inches(1.95), Inches(2.32), Inches(0.55), MID)
    tb(s, x + Inches(0.1), Inches(2.03), Inches(2.12), Inches(0.45),
       title, size=12.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tb(s, x + Inches(0.1), Inches(2.7), Inches(2.12), Inches(0.75),
       price, size=14, bold=True, color=DEEP, align=PP_ALIGN.CENTER, line_spacing=1.05)
    tb(s, x + Inches(0.1), Inches(3.55), Inches(2.12), Inches(1.1),
       desc, size=11, color=GRAY, align=PP_ALIGN.CENTER, line_spacing=1.15)
bullets(s, Inches(0.55), Inches(5.15), Inches(12.2), Inches(2.0), [
    ("Юнит-экономика: ", "LTV ~12–15 млн ₽ на клинику (5 лет), CAC 0,8–1,2 млн ₽ с учётом пилота; цикл сделки 6–9 мес."),
    ("Воронка: ", "научный контент → пилот на данных клиники (1–3 мес.) → сравнение прогноза с фактом → договор."),
    ("Lock-in: ", "глубокая интеграция с МИС и накопление исторических данных клиники повышают стоимость переключения."),
])

# ==================== 7. TRACTION / СТАТУС ====================
s = slide_chrome(7, "Статус проекта: прототип, ИС, команда, пилот 2026–27",
                 "Ключевые вехи достигнуты; следующий шаг — проспективная валидация и регистрация ИИ-МИ")
kpi_card(s, Inches(0.55), Inches(1.95), Inches(3.0), Inches(1.5), "AUC 0,89", "предварительная внутренняя валидация (требуется проспективное исследование)")
kpi_card(s, Inches(3.75), Inches(1.95), Inches(3.0), Inches(1.5), "6 РИД", "свидетельство №1440-028-537 (30.03.2026), ПОЭВМ, заявки, know-how")
kpi_card(s, Inches(6.95), Inches(1.95), Inches(3.0), Inches(1.5), "45 млн ₽", "оценка ИС для вклада в УК АО (отчёт оценщика)")
kpi_card(s, Inches(10.15), Inches(1.95), Inches(2.6), Inches(1.5), "8–10 тыс.", "циклов в пилоте: НМИЦ АГП + 5–7 клиник")
bullets(s, Inches(0.55), Inches(3.8), Inches(12.2), Inches(3.2), [
    ("Регуляторика: ", "подготовка к регистрации ПО как медизделия; рассмотрение режима «песочницы» ДЗМ/Минздрава для ИИ-МИ."),
    ("Инфраструктура: ", "доступ к циклам через НМИЦ АГП им. В. И. Кулакова; российское облако с требованиями 152-ФЗ."),
    ("Обезличивание: ", "PIPL-совместимая архитектура для будущего Китая; masking при неполных данных."),
    ("Роадмап: ", "2026–27 пилот и регистрация → 2028 модули и масштабирование на Москву → 2029 регионы и матчинг СМ → 2030 федеральный масштаб + Хайнань."),
    ("Доказательная база: ", "публикация результатов пилота в российских и международных изданиях — инструмент продаж и научной репутации."),
])

# ==================== 8. КОНКУРЕНЦЫ / УТП ====================
s = slide_chrome(8, "Конкурентное окружение и УТП",
                 "Коммерческие решения в РФ — в основном морфокинетика; глобальные лидеры — односекционные AI")
styled_table(s, Inches(0.55), Inches(1.9), Inches(12.25), Inches(2.6),
             ["Решение", "Страна", "Фокус данных", "Ограничение"],
             [
                 ["Ivy Fertility AI", "США", "Изображение + клиника", "Без мужского фактора / DFI, без РФ-адаптации"],
                 ["Life Whisperer / CooperSurgical", "США/Австр.", "Морфология эмбриона", "Однофокусность на «картинке»"],
                 ["Vitrolife Geri + AI", "Швеция", "Таймлапс + AI", "Аппаратная привязка, нет геномики"],
                 ["Fairtility CHLOE", "Израиль", "Таймлапс + AI", "Нет геномных и иммунных данных"],
                 ["ERICA / iDAScore (исследования)", "ЕС", "Морфология → плоидность", "Точность 70–81% без мультимодальности"],
                 ["VitaGen-AI", "РФ", "5 модальностей вкл. DFI и KIR/HLA-C", "Стадия валидации — закрывается пилотом"],
             ],
             col_ws=[3.2, 1.3, 2.6, 3.3], body_size=10.5)
bullets(s, Inches(0.55), Inches(4.85), Inches(12.2), Inches(2.2), [
    ("УТП: ", "единственная в РФ мультимодальная платформа (5 модальностей); интеграция DFI и иммунного матчинга KIR/HLA-C — по обзорным публикациям 2024–2025 гг. у коммерческих мировых аналогов не выявлена."),
    ("Точность: ", "рост AUC у мультимодальных моделей по обзорам — до +20–35% к однофакторным; наши предварительные 0,89 vs 0,65–0,72 у традиционных методов."),
    ("Суверенитет: ", "100% российская разработка, данные в РФ-облаке, замещение импортных решений в госсекторе."),
])

# ==================== 9. КОМАНДА ====================
s = slide_chrome(9, "Команда: клиника, наука, регуляторика, ИИ, международный рынок",
                 "Инициативная группа + план найма по раундам")
team = [
    ("Петрушина М. В.", "Генеральный директор", "Инициатор проекта, правообладатель РИД,\nООО «МедТехПрима»"),
    ("Изотов О. И., к.м.н.", "Научный консультант", "Российский университет медицины"),
    ("Смирнов С. Н., к.э.н.", "Экономика проекта", "Финансовый университет при Правительстве РФ"),
    ("Танделов А. Т.", "Регуляторика", "ГК «Глобальные Медицинские технологии»"),
    ("Воронцов А. И.", "Партнёрства", "ГК «Рич Кемикл», Академия Инноваторов"),
    ("Мороз А. Е.", "Развитие", "Академия Инноваторов"),
    ("N. Luo (КНР)", "Международный маркетинг", "АТР-направление, Хайнань"),
    ("Z. Abbas (Гонконг)", "Big Data / ML / AI", "IT-консалтинг платформы"),
]
for i, (name, role, desc) in enumerate(team):
    row, col_i = divmod(i, 4)
    x = Inches(0.55 + col_i * 3.15)
    y = Inches(1.9 + row * 1.8)
    rect(s, x, y, Inches(2.95), Inches(1.6), ICE, line=SKY)
    rect(s, x, y, Pt(5), Inches(1.6), MID)
    tb(s, x + Inches(0.18), y + Inches(0.12), Inches(2.65), Inches(0.35),
       name, size=13.5, bold=True, color=DEEP)
    tb(s, x + Inches(0.18), y + Inches(0.48), Inches(2.65), Inches(0.3),
       role, size=12, bold=True, color=MID)
    tb(s, x + Inches(0.18), y + Inches(0.82), Inches(2.65), Inches(0.65),
       desc, size=10.5, color=GRAY, line_spacing=1.1)
tb(s, Inches(0.55), Inches(5.65), Inches(12.2), Inches(1.3),
   "Научная база пилота: НМИЦ акушерства и гинекологии им. В. И. Кулакова и клиники-партнёры.\n"
   "Найм по Раунду 1: ML-инженеры (2–3), интеграционный разработчик, эмбриолог-аналитик,\n"
   "менеджер клинических исследований, регуляторный специалист; с 2027 — B2B-менеджер.",
   size=13.5, color=DARK, line_spacing=1.25)

# ==================== 10. ФИНАНСЫ ====================
s = slide_chrome(10, "Финансы: безубыточность 2028, выручка 391 млн ₽ к 2030",
                 "Базовый сценарий; переключатель в модели: пессимистичный / базовый / оптимистичный")
styled_table(s, Inches(0.55), Inches(1.9), Inches(12.25), Inches(2.9),
             ["Показатель, млн ₽", "2026", "2027", "2028", "2029", "2030"],
             [
                 ["Выручка", "7,1", "37,7", "113,7", "220,1", "391,1"],
                 ["Операционные расходы", "46,5", "70,5", "106,5", "167,0", "245,0"],
                 ["EBITDA", "−39,4", "−32,8", "+7,2", "+53,1", "+146,1"],
                 ["Чистая прибыль", "−39,5", "−32,8", "+6,8", "+50,4", "+138,8"],
                 ["Остаток денежных средств", "0,5", "20,8", "34,0", "91,1", "239,2"],
             ],
             col_ws=[3.4, 1, 1, 1, 1, 1], body_size=12)
kpi_card(s, Inches(0.55), Inches(5.05), Inches(3.0), Inches(1.5), "2028", "EBITDA-безубыточность и кассовый выход в плюс", val_color=MID)
kpi_card(s, Inches(3.75), Inches(5.05), Inches(3.0), Inches(1.5), "37%", "маржа EBITDA в 2030 г.")
kpi_card(s, Inches(6.95), Inches(5.05), Inches(3.0), Inches(1.5), "×0,75 / ×1,3", "песс. / опт. сценарии по выручке (расходы ×1,12 / ×0,95)")
kpi_card(s, Inches(10.15), Inches(5.05), Inches(2.6), Inches(1.5), "УСН 5%", "налог в модели (консервативно, без Сколково)")

# ==================== 11. ИНВЕСТИЦИИ ====================
s = slide_chrome(11, "Инвестиции: 70 млн ₽ за два раунда",
                 "Непубличное АО «ВИТА ГЕН АИ» · привилегированные акции · акционерное соглашение · опционный пул 12%")
# два раунда
rect(s, Inches(0.55), Inches(1.9), Inches(6.0), Inches(2.5), ICE, line=SKY)
rect(s, Inches(0.55), Inches(1.9), Inches(6.0), Inches(0.5), DEEP)
tb(s, Inches(0.75), Inches(1.97), Inches(5.6), Inches(0.4),
   "Раунд 1 · Seed · 2026", size=15, bold=True, color=WHITE)
bullets(s, Inches(0.75), Inches(2.55), Inches(5.6), Inches(1.7), [
    "35 млн ₽ · pre-money 110 млн ₽ (вкл. ИС 45 млн ₽)",
    "Доля инвестора: 24,1% (после Series A — 20,8%)",
    "Направления: ядро и интеграции 12 · валидация 7 · регуляторика 5 · команда 7 · ИС/юриспруденция 2,5 · резерв 1,5",
], size=12.5)
rect(s, Inches(6.8), Inches(1.9), Inches(6.0), Inches(2.5), ICE, line=SKY)
rect(s, Inches(6.8), Inches(1.9), Inches(6.0), Inches(0.5), MID)
tb(s, Inches(7.0), Inches(1.97), Inches(5.6), Inches(0.4),
   "Раунд 2 · Series A · 2027", size=15, bold=True, color=WHITE)
bullets(s, Inches(7.0), Inches(2.55), Inches(5.6), Inches(1.7), [
    "45 млн ₽ · pre-money 280 млн ₽",
    "Доля инвестора: 13,8%",
    "Направления: модули 2028, коммерческий запуск Москва, регионы, WFOE Хайнань и подготовка NMPA",
], size=12.5)
# эффективность
styled_table(s, Inches(0.55), Inches(4.55), Inches(7.7), Inches(1.95),
             ["Показатель", "Seed", "Series A"],
             [
                 ["Сумма", "35 млн ₽", "45 млн ₽"],
                 ["MOIC при выходе 2031", "8,0×", "4,2×"],
                 ["IRR", "≈52%", "≈43%"],
                 ["NPV @ 25% (Seed)", "45,6 млн ₽", "—"],
             ],
             col_ws=[3, 2, 2], body_size=11)
rect(s, Inches(8.5), Inches(4.55), Inches(4.3), Inches(1.95), DEEP)
tb(s, Inches(8.7), Inches(4.68), Inches(3.9), Inches(0.35),
   "Выход (2031)", size=13, bold=True, color=BRIGHT)
tb(s, Inches(8.7), Inches(5.08), Inches(3.9), Inches(1.3),
   "EBITDA 180 млн ₽ × 7,5 = 1 350 млн ₽\n"
   "Стратеги: IT/medtech-холдинги, лабораторные сети,\nВЭБ.РФ, IPO МСП-биржа",
   size=12, color=WHITE, line_spacing=1.2)
tb(s, Inches(0.55), Inches(6.6), Inches(12.2), Inches(0.4),
   "Дополнительно: гранты ФСИ/Сколково/ВЭБ.РФ/ДЗМ — 10–20 млн ₽ non-dilutive. Cap table post-Series A: 63,1% основатель/МедТехПрима · 20,8% Seed · 13,8% Series A · 8,9% опционный пул.",
   size=10.5, color=GRAY)

# ==================== 12. ROADMAP / КИТАЙ ====================
s = slide_chrome(12, "Дорожная карта 2026–2030 и международный трек",
                 "Федеральный масштаб поэтапно; экспорт через зону свободной торговли Хайнань")
years = [
    ("2026", "Seed", "Доработка ядра,\nинтеграции с МИС,\nстарт пилота", DEEP),
    ("2027", "Series A", "Пилот 8–10 тыс. циклов,\nрегистрация ИИ-МИ,\nпервые продажи", MID),
    ("2028", "Москва", "Модули niPGT-A/\nэндометрий/CLBR,\n~32 клиники", MID),
    ("2029", "Регионы + матчинг", "55 клиник, 3 региона B2G,\nматчинг СМ, WFOE Хайнань", BRIGHT),
    ("2030", "Федеральный + АТР", "85+ клиник, 391 млн ₽,\n3 APAC-партнёра,\nфайлинг NMPA", BRIGHT),
]
for i, (year, tag, desc, col) in enumerate(years):
    x = Inches(0.55 + i * 2.5)
    rect(s, x, Inches(1.95), Inches(2.32), Inches(0.55), col)
    tb(s, x, Inches(2.02), Inches(2.32), Inches(0.45),
       f"{year}  ·  {tag}", size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    rect(s, x, Inches(2.5), Inches(2.32), Inches(1.9), ICE, line=SKY)
    tb(s, x + Inches(0.1), Inches(2.65), Inches(2.12), Inches(1.6),
       desc, size=12, color=DARK, align=PP_ALIGN.CENTER, line_spacing=1.2)
rect(s, Inches(0.55), Inches(4.65), Inches(12.25), Inches(2.25), ICE, line=SKY)
tb(s, Inches(0.8), Inches(4.8), Inches(11.7), Inches(0.4),
   "Китайский трек (детали — раздел 10 бизнес-плана)", size=15, bold=True, color=DEEP)
bullets(s, Inches(0.8), Inches(5.25), Inches(11.7), Inches(1.5), [
    "2028 — gap-анализ NMPA, поиск партнёров · 2029 — регистрация WFOE, 1–2 пилотных партнёра (~8 млн ₽) · 2030 — 3 партнёра (~25,5 млн ₽)",
    "Льготный КН 15% (политика СПК Госсовета по Хайнаню), пилотный режим Боао Лэчэн, PIPL: локальный деплой, экспорт только агрегатов",
], size=13)

# ==================== 13. КОНТАКТЫ / CTA ====================
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, W, H, DEEP)
rect(s, 0, Inches(5.85), W, Pt(5), BRIGHT)
rect(s, 0, Inches(5.9), W, Inches(1.6), MID)
tb(s, Inches(0.9), Inches(1.3), Inches(11.5), Inches(1.0),
   "Соединим клинику, генетику и ИИ —\nчтобы каждый цикл ВРТ давал ребёнка",
   size=30, bold=True, color=WHITE, line_spacing=1.2)
tb(s, Inches(0.9), Inches(3.3), Inches(11.5), Inches(2.2),
   "Seeking:  Seed 35 млн ₽ (2026) + Series A 45 млн ₽ (2027)\n"
   "Структура:  непубличное АО, привилегированные акции, акционерное соглашение, опционный пул 12%\n"
   "Готовы:  due diligence, пилотный протокол, отчёт оценщика по ИС, model deck",
   size=16, color=SKY, line_spacing=1.4)
tb(s, Inches(0.9), Inches(6.15), Inches(7.5), Inches(1.1),
   "Петрушина Марина Владимировна · генеральный директор\n"
   "ООО «МедТехПрима»  ·  проектная компания: АО «ВИТА ГЕН АИ» (создаётся)\n"
   "+7 985 728 66 55  ·  mar.petrushina@yandex.ru",
   size=15, color=WHITE, line_spacing=1.3)
tb(s, W - Inches(3.6), Inches(6.4), Inches(2.9), Inches(0.8),
   "VitaGen-AI · 2026\nКоммерческая тайна",
   size=13, color=SKY, align=PP_ALIGN.RIGHT, line_spacing=1.2)

out = r"C:\Users\User\Documents\Freelance\Business plan\Готовые документы\VitaGen_Инвестиционная_презентация.pptx"
prs.save(out)
print("saved:", out)
