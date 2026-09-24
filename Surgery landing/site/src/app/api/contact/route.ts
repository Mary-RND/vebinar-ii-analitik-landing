import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { name, contact, interest, comment } = body as Record<string, string>;

    if (!name || !contact) {
      return NextResponse.json({ ok: false, error: "missing fields" }, { status: 400 });
    }

    const to = process.env.CONTACT_TO || "hello@example.ru";
    const subject = `Запрос с сайта — ${interest || "без направления"} — ${name}`;

    // В проде подключить Resend / Nodemailer / SMTP. Пока — лог в консоль сервера.
    console.log("[contact]", { to, subject, name, contact, interest, comment });

    // TODO: заменить на реальную отправку:
    // await resend.emails.send({ from: "site@example.ru", to, subject, text: ... })

    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ ok: false }, { status: 500 });
  }
}