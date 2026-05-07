# DisparoEmailG4

SaaS pessoal (single-user) para disparo de e-mails em massa com CTA de WhatsApp.

## Funcionalidades
- Colar lista de e-mails (linha, vírgula, ponto e vírgula ou misto)
- Validação, deduplicação e preview dos destinatários
- Editor de mensagem (HTML simples) com preview
- Variável `{{EMAIL}}` para personalização
- Templates salvos em SQLite com Prisma
- Configuração SMTP com teste de conexão
- CTA de WhatsApp automática no rodapé do e-mail
- Envio com delay aleatório configurável e progresso em tempo real
- Botão para interromper campanha
- Histórico de campanhas em SQLite

## Requisitos
- Node.js 20+
- npm

## Instalação local
1. Clone o projeto.
2. Crie o arquivo `.env` com base no `.env.example`.
3. Instale dependências:
   ```bash
   npm install
   ```
4. Gere o Prisma client e banco:
   ```bash
   npx prisma migrate dev --name init
   ```
5. Rode em desenvolvimento:
   ```bash
   npm run dev
   ```
6. Acesse `http://localhost:3000`.

## Variáveis de ambiente
```env
DATABASE_URL="file:./prisma/dev.db"
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="seuemail@gmail.com"
SMTP_PASS="sua_app_password"
SENDER_NAME="Seu Nome"
WHATSAPP_NUMBER="+5511999999999"
WHATSAPP_CTA_TEXT="Quer conversar? Clique aqui e fale comigo no WhatsApp!"
WHATSAPP_DEFAULT_MESSAGE="Olá! Vim pelo seu e-mail e quero conversar."
```

## Gmail App Password (passo a passo)
1. Entre em `https://myaccount.google.com/` com sua conta Gmail.
2. Vá em **Segurança**.
3. Ative a **Verificação em duas etapas** (obrigatório).
4. Ainda em Segurança, abra **Senhas de app**.
5. Selecione **App** (ex.: Mail) e **Dispositivo** (ex.: Outro nome: DisparoEmailG4).
6. Clique em **Gerar**.
7. Copie a senha de 16 caracteres e use no campo `SMTP_PASS` ou no formulário da aplicação.

## Deploy com Docker
```bash
docker build -t disparoemailg4 .
docker run -p 3000:3000 --env-file .env disparoemailg4
```

## Deploy com Vercel
1. Faça push do projeto para GitHub.
2. Importe no Vercel.
3. Configure as mesmas variáveis de ambiente do `.env` no painel do Vercel.
4. Rode o comando de build padrão (`npm run build`).

> Observação: o banco SQLite é local. Em ambiente serverless, prefira volume persistente ou trocar para banco gerenciado.
