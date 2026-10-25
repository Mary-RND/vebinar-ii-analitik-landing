import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

export default function Page() {
  return (
    <>
      <Header />
      <main className="mx-auto max-w-3xl px-5 py-28 sm:px-8">
        <h1 className="font-display text-3xl font-medium">Политика конфиденциальности</h1>
        <p className="mt-4 text-sm leading-relaxed text-ink/60">
          Заглушка. Замените на вашу политику обработки персональных данных.
        </p>
      </main>
      <Footer />
    </>
  );
}