# Weekly Report Automation

Lê um arquivo `.md` do Google Drive, formata via GPT-4o e envia por e-mail toda sexta-feira às 17h (Brasília).

## Pré-requisitos

- Python 3.11+
- Conta Railway
- Conta Google Cloud (gratuita)
- Gmail com 2FA ativado

## Instalação local

```bash
git clone <repo>
cd weekly-report
pip install -r requirements.txt
cp .env.example .env
# edite o .env com suas credenciais
python main.py
```

## Configuração

### 1. Google Drive API — Service Account

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto ou selecione um existente
3. Vá em **APIs & Services → Library**, busque **Google Drive API** e clique em **Enable**
4. Vá em **APIs & Services → Credentials → Create Credentials → Service Account**
5. Dê um nome à service account e clique em **Done**
6. Clique na service account criada → aba **Keys** → **Add Key → Create new key → JSON**
7. Baixe o arquivo JSON
8. No Google Drive, **compartilhe a pasta `Reports`** com o e-mail da service account (ex: `nome@projeto.iam.gserviceaccount.com`) com permissão **Viewer**
9. Cole o conteúdo completo do JSON (em uma linha) na variável `GOOGLE_SERVICE_ACCOUNT_JSON` do `.env`

### 2. Gmail App Password

1. Acesse [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Selecione **Mail** e o dispositivo, clique em **Generate**
3. Copie a senha de 16 caracteres para `GMAIL_APP_PASSWORD`

> O 2FA precisa estar ativado na conta Google para App Passwords funcionar.

### 3. Variáveis de ambiente

Copie `.env.example` para `.env` e preencha todos os campos. Veja os comentários no arquivo para instruções detalhadas de cada variável.

## Estrutura esperada no Google Drive

```
Reports/
└── 2026/
    ├── Semana1.md
    ├── Semana2.md
    └── ...
```

O script detecta automaticamente o número da semana ISO atual e busca o arquivo correspondente.

> Se você usa o Google Drive Desktop (espelhamento local), a pasta `Reports` aparece como `Computadores/Meu laptop/.../Reports` no Drive. O script busca diretamente pelo nome `Reports` — não importa onde ela esteja na hierarquia raiz.

## Deploy no Railway

1. Faça push do repositório para o GitHub
2. Acesse [railway.app](https://railway.app) → **New Project → Deploy from GitHub repo**
3. Selecione o repositório
4. Vá em **Variables** e adicione todas as variáveis do `.env`
5. O `railway.toml` já configura o cron: toda sexta-feira às 17h (horário de Brasília / 20h UTC)

Para verificar se o cron está ativo: **Settings → Cron Schedule** deve mostrar `0 20 * * 5`.

## Execução manual

```bash
python main.py
```

Logs mostram cada etapa com emojis. Se o arquivo da semana não for encontrado, o script encerra com exit code 1.

## Formato do arquivo .md

Veja o exemplo em [`template/semana-exemplo.md`](template/semana-exemplo.md).

Seções suportadas:
- `## Engenharia de Dados`
- `## IA & Modelos`
- `## Estudos`
- `## Reuniões`
- `## Bloqueios`
- `## Próxima semana`

Seções vazias são omitidas automaticamente do e-mail.
