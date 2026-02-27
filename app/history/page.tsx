import Link from "next/link";

export default function HistoryPage() {
  return (
    <main className="mx-auto max-w-4xl p-6">
      <h1 className="text-2xl font-bold">Histórico</h1>
      <p className="mt-2">Use a aba Histórico na página principal.</p>
      <Link href="/" className="mt-4 inline-block text-blue-600">Voltar</Link>
    </main>
  );
}
