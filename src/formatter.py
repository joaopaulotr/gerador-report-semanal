import base64
import json
import logging
from pathlib import Path
from typing import Optional
from openai import OpenAI
import config

logger = logging.getLogger(__name__)
_client = OpenAI(api_key=config.OPENAI_API_KEY)

SYSTEM_PROMPT = """Você transforma notas brutas de engenheiro de dados em relatório semanal profissional.

Retorne APENAS um JSON com esta estrutura exata:
{
  "week": "número da semana extraído do cabeçalho",
  "date_range": "período extraído do cabeçalho (ex: 19/05 a 23/05/2026)",
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

# P+Solution brand colors (extraídos da logo)
BLUE = "#4A6FBF"
TEAL = "#00BFA0"
TEXT = "#2d2d2d"
TEXT_LIGHT = "#666666"
BG = "#f5f6f8"


def _load_logo_b64() -> Optional[str]:
    logo_path = Path(__file__).parent.parent / "template" / "Logo2025 1.png"
    logger.info(f"Logo path: {logo_path.resolve()} — exists: {logo_path.exists()}")
    if not logo_path.exists():
        logger.warning("Logo file not found, skipping")
        return None
    b64 = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
    logger.info(f"Logo loaded: {len(b64)} base64 chars")
    return b64


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


def _build_html(data: dict, logo_b64: Optional[str]) -> str:
    sections = (
        _section("Tarefas Realizadas", data.get("tasks", []))
        + _section("Bloqueios", data.get("blockers", []))
        + _section("Próxima Semana", data.get("next_week", []))
    )

    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" alt="P+Solution" height="48" style="display: block;" />'
        if logo_b64
        else f'<span style="font-family: Calibri, Arial, sans-serif; font-size: 18px; font-weight: 700; color: {BLUE};">P+Solution Research</span>'
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
              {logo_html}
            </td>
          </tr>

          <!-- Header semana -->
          <tr>
            <td style="padding: 20px 32px 8px 32px; background-color: #ffffff;">
              <p style="margin: 0; font-family: Calibri, Arial, sans-serif; font-size: 11px; font-weight: 400; letter-spacing: 1.5px; text-transform: uppercase; color: {TEXT_LIGHT};">Relatório Semanal</p>
              <p style="margin: 4px 0 0 0; font-family: Calibri, Arial, sans-serif; font-size: 22px; font-weight: 700; color: {BLUE};">Semana {data.get("week", "")} &nbsp;&middot;&nbsp; {data.get("date_range", "")}</p>
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
    logo_b64 = _load_logo_b64()
    html = _build_html(data, logo_b64)
    logger.info(f"HTML formatted ({len(html)} chars)")
    return html
