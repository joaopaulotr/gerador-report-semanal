import json
import logging
from datetime import date, timedelta
from openai import OpenAI
import config

logger = logging.getLogger(__name__)
_client = OpenAI(api_key=config.OPENAI_API_KEY)

SYSTEM_PROMPT = """Você transforma notas brutas de engenheiro de dados em relatório semanal profissional.

Retorne APENAS um JSON com esta estrutura exata:
{
  "tasks": ["tarefa reescrita 1", "tarefa reescrita 2"],
  "blockers": ["bloqueio 1"],
  "next_week": ["item 1", "item 2"]
}

Regras para reescrever as tarefas em "tasks":
- Consolide tudo que foi feito: engenharia, IA, estudos, reuniões — lista única
- Tom profissional direto, padrão mercado de trabalho tech
- Preserve todas as métricas e números exatamente como estão (ex: AUC 0.87, redução de 40%)
- Reescreva como entrega concluída, não como nota pessoal
- Se bloqueios ou próxima semana não tiverem conteúdo, retorne lista vazia []
- Não invente informação que não esteja nas notas"""


def _current_week_info() -> tuple:
    today = date.today()
    week = today.isocalendar()[1]
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    date_range = f"{monday.strftime('%d/%m')} a {friday.strftime('%d/%m/%Y')}"
    return week, date_range

# P+Solution brand colors (extraídos da logo)
BLUE = "#4A6FBF"
TEAL = "#00BFA0"
TEXT = "#2d2d2d"
TEXT_LIGHT = "#666666"
BG = "#f5f6f8"

LOGO_URL = "https://raw.githubusercontent.com/joaopaulotr/gerador-report-semanal/main/template/Logo2025%201.png"


def _li_items(items: list) -> str:
    return "".join(
        f'<li style="margin-bottom: 8px; color: {TEXT};">{item}</li>'
        for item in items
    )


def _section(title: str, items: list) -> str:
    if not items:
        return ""
    return f"""<div style="margin-bottom: 28px;">
      <h2 style="margin: 0 0 12px 0; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: {BLUE}; border-bottom: 2px solid {TEAL}; padding-bottom: 6px; font-family: Calibri, Arial, sans-serif;">{title}</h2>
      <ul style="margin: 10px 0 0 0; padding-left: 20px; font-size: 14px; line-height: 1.8; font-family: Calibri, Arial, sans-serif;">
        {_li_items(items)}
      </ul>
    </div>"""


def _build_html(data: dict, week: int, date_range: str) -> str:
    sections = (
        _section("Tarefas Realizadas", data.get("tasks", []))
        + _section("Bloqueios", data.get("blockers", []))
        + _section("Próxima Semana", data.get("next_week", []))
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<body style="margin: 0; padding: 0; background-color: {BG};">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: {BG};">
    <tr>
      <td align="center" style="padding: 32px 16px;">
        <table width="640" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 2px; box-shadow: 0 1px 4px rgba(0,0,0,0.08);">

          <!-- Logo -->
          <tr>
            <td style="padding: 24px 32px 16px 32px; border-bottom: 3px solid {TEAL};">
              <img src="{LOGO_URL}" alt="P+Solution" height="48" style="display: block;" />
            </td>
          </tr>

          <!-- Header semana -->
          <tr>
            <td style="padding: 20px 32px 8px 32px; background-color: #ffffff;">
              <p style="margin: 0; font-family: Calibri, Arial, sans-serif; font-size: 11px; font-weight: 400; letter-spacing: 1.5px; text-transform: uppercase; color: {TEXT_LIGHT};">Relatório Semanal</p>
              <p style="margin: 4px 0 0 0; font-family: Calibri, Arial, sans-serif; font-size: 22px; font-weight: 700; color: {BLUE};">Semana {week} &nbsp;&middot;&nbsp; {date_range}</p>
            </td>
          </tr>

          <!-- Divisor -->
          <tr>
            <td style="padding: 0 32px 24px 32px;">
              <div style="height: 1px; background-color: #e8e8e8; margin-top: 16px;"></div>
            </td>
          </tr>

          <!-- Conteúdo -->
          <tr>
            <td style="padding: 0 32px 32px 32px;">
              {sections}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 16px 32px; background-color: #f9f9f9; border-top: 1px solid #e8e8e8;">
              <p style="margin: 0; font-family: Calibri, Arial, sans-serif; font-size: 11px; color: {TEXT_LIGHT};">P+Solution Research &nbsp;&middot;&nbsp; Engenharia de Dados &amp; IA</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def format_report(raw_content: str) -> str:
    logger.info("Sending content to GPT-4o for formatting")

    response = _client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Transforme o seguinte relatório:\n\n{raw_content}"},
        ],
    )

    data = json.loads(response.choices[0].message.content)
    week, date_range = _current_week_info()
    html = _build_html(data, week, date_range)
    logger.info(f"HTML formatted — Semana {week} | {date_range} ({len(html)} chars)")
    return html
