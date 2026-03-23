import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DisparoEmailG4",
  description: "SaaS pessoal para disparo de campanhas por e-mail"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
