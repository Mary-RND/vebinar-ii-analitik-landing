"use client";

import { useState } from "react";
import { site } from "@/lib/site";

type Status = "idle" | "sending" | "ok" | "error";

export function ContactForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const payload = Object.fromEntries(fd.entries());

    if (!payload.name || !payload.contact) {
      setError("Пожалуйста, проверьте данные. Нам нужен хотя бы один способ, чтобы связаться с вами.");
      return;
    }

    setStatus("sending");
    setError(null);

    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error();
      setStatus("ok");
      (e.target as HTMLFormElement).reset();
    } catch {
      setStatus("error");
      setError(
        `Что-то пошло не так на нашей стороне. Пожалуйста, попробуйте ещё раз или напишите нам напрямую в Telegram: ${site.telegram}. Мы обязательно ответим.`
      );
    }
  }

  if (status === "ok") {
    return (
      <div className="rounded-2xl bg-emerald/5 p-8 ring-1 ring-emerald/20">
        <p className="font-medium text-emerald">Спасибо. Ваш запрос принят.</p>
        <p className="mt-2 text-sm leading-relaxed text-ink/65">
          Я лично ознакомлюсь с ним. Мы свяжемся с вами в течение рабочего дня, чтобы
          договориться о времени консультации. Если вопрос требует срочности, вы можете
          позвонить нам напрямую:{" "}
          <a href={site.phoneHref} className="font-semibold text-emerald hover:underline">
            {site.phone}
          </a>
          .
        </p>
        <button
          onClick={() => setStatus("idle")}
          className="mt-6 text-sm font-semibold text-bronze hover:text-terracotta"
        >
          Отправить ещё один запрос →
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-5">
      <div>
        <label htmlFor="name" className="text-sm font-medium text-ink/80">
          Как к вам обращаться?
        </label>
        <input
          id="name"
          name="name"
          placeholder="Ваше имя"
          autoComplete="name"
          className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm outline-none transition placeholder:text-ink/30 focus:border-bronze focus:ring-2 focus:ring-bronze/20"
        />
      </div>

      <div>
        <label htmlFor="contact" className="text-sm font-medium text-ink/80">
          Удобный способ связи
        </label>
        <input
          id="contact"
          name="contact"
          placeholder="Телефон или Telegram"
          autoComplete="tel"
          className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm outline-none transition placeholder:text-ink/30 focus:border-bronze focus:ring-2 focus:ring-bronze/20"
        />
      </div>

      <div>
        <label htmlFor="interest" className="text-sm font-medium text-ink/80">
          Что вас интересует?
        </label>
        <select
          id="interest"
          name="interest"
          defaultValue=""
          className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm outline-none transition focus:border-bronze focus:ring-2 focus:ring-bronze/20"
        >
          <option value="" disabled>
            Выберите направление
          </option>
          <option>Пластика лица</option>
          <option>Пластика тела</option>
          <option>Послеродовое восстановление</option>
          <option>Мужская пластика</option>
          <option>Пока просто изучаю вопрос</option>
        </select>
      </div>

      <div>
        <label htmlFor="comment" className="text-sm font-medium text-ink/80">
          Комментарий <span className="font-normal text-ink/40">(необязательно)</span>
        </label>
        <textarea
          id="comment"
          name="comment"
          rows={4}
          placeholder="Коротко опишите ваш запрос или задайте вопрос, если хотите подготовиться к разговору заранее..."
          className="mt-2 w-full resize-none rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm outline-none transition placeholder:text-ink/30 focus:border-bronze focus:ring-2 focus:ring-bronze/20"
        />
      </div>

      {error && (
        <p className="rounded-xl bg-red-50 px-4 py-3 text-sm leading-relaxed text-red-700 ring-1 ring-red-200">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={status === "sending"}
        className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-terracotta px-7 py-4 text-sm font-semibold text-ivory shadow-[0_12px_30px_-14px_rgba(184,115,79,0.7)] transition hover:bg-bronze disabled:opacity-60 sm:w-auto"
      >
        {status === "sending" ? "Отправляем..." : "Отправить запрос"}
        <span aria-hidden>→</span>
      </button>

      <p className="text-xs leading-relaxed text-ink/40">
        Нажимая кнопку, вы соглашаетесь с{" "}
        <a href="/policy" className="underline decoration-ink/20 underline-offset-4 hover:decoration-ink/40">
          политикой конфиденциальности
        </a>
        . Ваши данные в безопасности и используются только для связи с вами.
      </p>

      {status === "error" && !error && (
        <p className="text-sm text-red-600">Не удалось отправить. Попробуйте ещё раз.</p>
      )}
    </form>
  );
}