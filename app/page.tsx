"use client";

import { useEffect, useMemo, useState } from "react";
import { parseEmails } from "@/lib/email";
import { SendStatus, Template } from "@/lib/types";
import { Tabs } from "@/components/Tabs";

const PROVIDERS = {
  gmail: { host: "smtp.gmail.com", port: 587 },
  outlook: { host: "smtp.office365.com", port: 587 },
  custom: { host: "", port: 587 }
};

export default function Home() {
  const [tab, setTab] = useState("destinatarios");
  const [recipientsRaw, setRecipientsRaw] = useState("");
  const [subject, setSubject] = useState("");
  const [bodyHtml, setBodyHtml] = useState("<p>Olá {{EMAIL}},</p><p>Tenho uma proposta para você.</p>");
  const [templateName, setTemplateName] = useState("");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [provider, setProvider] = useState<"gmail" | "outlook" | "custom">("gmail");
  const [smtpHost, setSmtpHost] = useState(PROVIDERS.gmail.host);
  const [smtpPort, setSmtpPort] = useState(String(PROVIDERS.gmail.port));
  const [smtpUser, setSmtpUser] = useState("samuel.regente@g4educacao.com");
  const [smtpPass, setSmtpPass] = useState("");
  const [senderName, setSenderName] = useState("Samuel-G4");
  const [whatsappNumber, setWhatsappNumber] = useState("+5511970917705");
  const [whatsappCtaText, setWhatsappCtaText] = useState("Quer conversar? Clique aqui e fale comigo no WhatsApp!");
  const [whatsappMessage, setWhatsappMessage] = useState("Olá! Vim pelo seu e-mail e quero conversar.");
  const [delayMinMs, setDelayMinMs] = useState("3000");
  const [delayMaxMs, setDelayMaxMs] = useState("5000");
  const [testMessage, setTestMessage] = useState("");
  const [sendMessage, setSendMessage] = useState("");
  const [jobId, setJobId] = useState("");
  const [status, setStatus] = useState<SendStatus | null>(null);

  const parsed = useMemo(() => parseEmails(recipientsRaw), [recipientsRaw]);

  const loadTemplates = async () => {
    const response = await fetch("/api/templates");
    const data = await response.json();
    setTemplates(data.templates || []);
  };

  useEffect(() => {
    loadTemplates();
    const saved = localStorage.getItem("smtp-config-disparoemailg4");
    if (saved) {
      const cfg = JSON.parse(saved);
      setProvider(cfg.provider || "gmail");
      setSmtpHost(cfg.smtpHost || PROVIDERS.gmail.host);
      setSmtpPort(cfg.smtpPort || "587");
      setSmtpUser(cfg.smtpUser || "");
      setSenderName(cfg.senderName || "Samuel-G4");
      setWhatsappNumber(cfg.whatsappNumber || "+5511970917705");
      setWhatsappCtaText(cfg.whatsappCtaText || "Quer conversar? Clique aqui e fale comigo no WhatsApp!");
      setWhatsappMessage(cfg.whatsappMessage || "Olá! Vim pelo seu e-mail e quero conversar.");
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(
      "smtp-config-disparoemailg4",
      JSON.stringify({ provider, smtpHost, smtpPort, smtpUser, senderName, whatsappNumber, whatsappCtaText, whatsappMessage })
    );
  }, [provider, smtpHost, smtpPort, smtpUser, senderName, whatsappNumber, whatsappCtaText, whatsappMessage]);

  useEffect(() => {
    if (!jobId) return;
    const timer = setInterval(async () => {
      const response = await fetch(`/api/send/status/${jobId}`);
      if (!response.ok) return;
      const data = await response.json();
      setStatus(data.status);
      if (data.status.finished) {
        setSendMessage("Campanha finalizada.");
        clearInterval(timer);
      }
    }, 1200);
    return () => clearInterval(timer);
  }, [jobId]);

  const saveTemplate = async () => {
    const response = await fetch("/api/templates", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: templateName, subject, body: bodyHtml })
    });
    const data = await response.json();
    if (!response.ok) {
      setSendMessage(data.error);
      return;
    }
    setTemplateName("");
    loadTemplates();
  };

  const testConnection = async () => {
    setTestMessage("Testando...");
    const response = await fetch("/api/send/test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ host: smtpHost, port: Number(smtpPort), user: smtpUser, pass: smtpPass, senderName })
    });
    const data = await response.json();
    setTestMessage(response.ok ? data.message : data.error);
  };

  const startCampaign = async () => {
    setSendMessage("Iniciando envio...");
    const response = await fetch("/api/send/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        recipientsRaw,
        subject,
        bodyHtml,
        senderName,
        senderEmail: smtpUser,
        whatsappNumber,
        whatsappCtaText,
        whatsappMessage,
        delayMinMs: Number(delayMinMs),
        delayMaxMs: Number(delayMaxMs),
        smtp: {
          host: smtpHost,
          port: Number(smtpPort),
          user: smtpUser,
          pass: smtpPass
        }
      })
    });
    const data = await response.json();
    if (!response.ok) {
      setSendMessage(data.error);
      return;
    }
    setJobId(data.id);
    setSendMessage(`Campanha iniciada. ${data.validCount} e-mails válidos.`);
  };

  const stopCampaign = async () => {
    if (!jobId) return;
    await fetch(`/api/send/stop/${jobId}`, { method: "POST" });
    setSendMessage("Solicitação de parada enviada.");
  };

  return (
    <main className="mx-auto max-w-6xl p-6">
      <h1 className="mb-2 text-3xl font-bold">DisparoEmailG4</h1>
      <p className="mb-6 text-slate-600">Ferramenta pessoal de disparo de e-mail para campanhas de vendas.</p>

      <Tabs
        tabs={[
          { id: "destinatarios", label: "1 — Destinatários" },
          { id: "mensagem", label: "2 — Mensagem" },
          { id: "config", label: "3 — Configurações" },
          { id: "enviar", label: "4 — Enviar" },
          { id: "historico", label: "Histórico" }
        ]}
        active={tab}
        onChange={setTab}
      />

      {tab === "destinatarios" && (
        <section className="rounded-xl bg-white p-6 shadow">
          <h2 className="mb-3 text-xl font-semibold">Cole a lista de e-mails</h2>
          <textarea className="h-56 w-full rounded border p-3" value={recipientsRaw} onChange={(e) => setRecipientsRaw(e.target.value)} />
          <p className="mt-3 text-sm">Válidos: <strong>{parsed.valid.length}</strong> | Inválidos: <strong>{parsed.invalid.length}</strong></p>
          {parsed.invalid.length > 0 && <p className="mt-2 text-sm text-red-600">Inválidos: {parsed.invalid.join(", ")}</p>}
          <div className="mt-4 max-h-40 overflow-auto rounded bg-slate-50 p-3 text-sm">
            {parsed.valid.map((email) => <div key={email}>{email}</div>)}
          </div>
        </section>
      )}

      {tab === "mensagem" && (
        <section className="grid gap-5 rounded-xl bg-white p-6 shadow md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-semibold">Assunto</label>
            <input className="mb-3 w-full rounded border p-2" value={subject} onChange={(e) => setSubject(e.target.value)} />
            <label className="mb-1 block text-sm font-semibold">Corpo (HTML simples)</label>
            <textarea className="h-72 w-full rounded border p-3" value={bodyHtml} onChange={(e) => setBodyHtml(e.target.value)} />
            <p className="mt-2 text-xs text-slate-500">Use {'{{EMAIL}}'} para personalizar por destinatário.</p>
            <div className="mt-4 flex gap-2">
              <input className="flex-1 rounded border p-2" placeholder="Nome do template" value={templateName} onChange={(e) => setTemplateName(e.target.value)} />
              <button className="rounded bg-blue-600 px-3 py-2 text-white" onClick={saveTemplate}>Salvar template</button>
            </div>
            <div className="mt-3 space-y-2">
              {templates.map((template) => (
                <button key={template.id} className="block w-full rounded border p-2 text-left" onClick={() => { setSubject(template.subject); setBodyHtml(template.body); }}>
                  {template.name}
                </button>
              ))}
            </div>
          </div>
          <div>
            <h3 className="mb-2 font-semibold">Preview</h3>
            <div className="min-h-72 rounded border bg-slate-50 p-4" dangerouslySetInnerHTML={{ __html: bodyHtml }} />
          </div>
        </section>
      )}

      {tab === "config" && (
        <section className="space-y-6 rounded-xl bg-white p-6 shadow">
          <details open>
            <summary className="cursor-pointer text-lg font-semibold">Configuração SMTP</summary>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              <label className="text-sm">Provedor
                <select className="mt-1 w-full rounded border p-2" value={provider} onChange={(e) => {
                  const value = e.target.value as "gmail" | "outlook" | "custom";
                  setProvider(value);
                  setSmtpHost(PROVIDERS[value].host);
                  setSmtpPort(String(PROVIDERS[value].port));
                }}>
                  <option value="gmail">Gmail</option>
                  <option value="outlook">Outlook</option>
                  <option value="custom">SMTP customizado</option>
                </select>
              </label>
              <label className="text-sm">Host
                <input className="mt-1 w-full rounded border p-2" value={smtpHost} onChange={(e) => setSmtpHost(e.target.value)} />
              </label>
              <label className="text-sm">Porta
                <input className="mt-1 w-full rounded border p-2" value={smtpPort} onChange={(e) => setSmtpPort(e.target.value)} />
              </label>
              <label className="text-sm">E-mail remetente
                <input className="mt-1 w-full rounded border p-2" value={smtpUser} onChange={(e) => setSmtpUser(e.target.value)} />
              </label>
              <label className="text-sm">Senha / app password
                <input type="password" className="mt-1 w-full rounded border p-2" value={smtpPass} onChange={(e) => setSmtpPass(e.target.value)} />
              </label>
              <label className="text-sm">Nome de exibição
                <input className="mt-1 w-full rounded border p-2" value={senderName} onChange={(e) => setSenderName(e.target.value)} />
              </label>
            </div>
            <button className="mt-4 rounded bg-emerald-600 px-4 py-2 text-white" onClick={testConnection}>Testar conexão</button>
            {testMessage && <p className="mt-2 text-sm">{testMessage}</p>}
          </details>

          <details open>
            <summary className="cursor-pointer text-lg font-semibold">WhatsApp CTA</summary>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              <label className="text-sm">Número WhatsApp
                <input className="mt-1 w-full rounded border p-2" value={whatsappNumber} onChange={(e) => setWhatsappNumber(e.target.value)} />
              </label>
              <label className="text-sm">Texto do botão
                <input className="mt-1 w-full rounded border p-2" value={whatsappCtaText} onChange={(e) => setWhatsappCtaText(e.target.value)} />
              </label>
              <label className="text-sm md:col-span-2">Mensagem pré-preenchida
                <input className="mt-1 w-full rounded border p-2" value={whatsappMessage} onChange={(e) => setWhatsappMessage(e.target.value)} />
              </label>
            </div>
          </details>
        </section>
      )}

      {tab === "enviar" && (
        <section className="rounded-xl bg-white p-6 shadow">
          <h2 className="mb-2 text-xl font-semibold">Revisão e envio</h2>
          <p className="text-sm">Destinatários válidos: <strong>{parsed.valid.length}</strong></p>
          <p className="text-sm">Assunto: <strong>{subject || "(sem assunto)"}</strong></p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <label className="text-sm">Delay mínimo (ms)
              <input className="mt-1 w-full rounded border p-2" value={delayMinMs} onChange={(e) => setDelayMinMs(e.target.value)} />
            </label>
            <label className="text-sm">Delay máximo (ms)
              <input className="mt-1 w-full rounded border p-2" value={delayMaxMs} onChange={(e) => setDelayMaxMs(e.target.value)} />
            </label>
          </div>
          <div className="mt-4 flex gap-2">
            <button className="rounded bg-blue-700 px-4 py-2 font-semibold text-white" onClick={startCampaign}>Disparar Campanha</button>
            <button className="rounded bg-rose-700 px-4 py-2 font-semibold text-white" onClick={stopCampaign}>Parar</button>
          </div>
          {sendMessage && <p className="mt-3 text-sm">{sendMessage}</p>}
          {status && (
            <div className="mt-4 rounded border bg-slate-50 p-3 text-sm">
              <p>Enviando {status.sent + status.failed}/{status.total}... {status.current ? `✓ ${status.current}` : ""}</p>
              <p>Sucesso: {status.sent} | Falhas: {status.failed}</p>
              {status.finished && <p className="font-semibold">Concluído {status.stopped ? "(interrompido)" : ""}</p>}
              {status.failures.length > 0 && <p>Falhas: {status.failures.map((item) => item.email).join(", ")}</p>}
            </div>
          )}
        </section>
      )}

      {tab === "historico" && <HistoryTab />}
    </main>
  );
}

function HistoryTab() {
  const [campaigns, setCampaigns] = useState<any[]>([]);

  useEffect(() => {
    fetch("/api/campaigns")
      .then((res) => res.json())
      .then((data) => setCampaigns(data.campaigns || []));
  }, []);

  return (
    <section className="rounded-xl bg-white p-6 shadow">
      <h2 className="mb-4 text-xl font-semibold">Histórico de campanhas</h2>
      <div className="space-y-3">
        {campaigns.map((campaign) => (
          <div key={campaign.id} className="rounded border p-3">
            <p className="font-semibold">{campaign.subject}</p>
            <p className="text-sm">{new Date(campaign.sentAt).toLocaleString("pt-BR")}</p>
            <p className="text-sm">Destinatários: {campaign.recipientsCount} | Sucesso: {campaign.successCount} | Falhas: {campaign.failureCount}</p>
          </div>
        ))}
        {campaigns.length === 0 && <p className="text-sm text-slate-500">Nenhuma campanha enviada ainda.</p>}
      </div>
    </section>
  );
}
