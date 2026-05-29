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


def _bullet_rows(items: list) -> str:
    rows = []
    for item in items:
        rows.append(
            f'<tr>'
            f'<td width="20" valign="top"'
            f' style="font-family: Arial, sans-serif; font-size: 16px; line-height: 22px;'
            f' color: #00E5C4; padding: 0 0 10px 0; mso-line-height-rule: exactly;">&#8250;</td>'
            f'<td valign="top"'
            f' style="font-family: Arial, sans-serif; font-size: 14px; line-height: 22px;'
            f' color: #D1D5DB; padding: 0 0 10px 0; mso-line-height-rule: exactly;">{item}</td>'
            f'</tr>'
        )
    return "".join(rows)


def _section(title: str, items: list) -> str:
    if not items:
        return ""
    return (
        f'<table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">'
        f'<tr>'
        f'<td width="3" bgcolor="#00E5C4"'
        f' style="background-color: #00E5C4; font-size: 1px; line-height: 1px;">&nbsp;</td>'
        f'<td style="padding: 0 0 0 14px;">'
        f'<p style="margin: 0; mso-margin-top-alt: 0; mso-margin-bottom-alt: 0;'
        f' font-family: Arial, sans-serif; font-size: 10px; font-weight: 700;'
        f' text-transform: uppercase; letter-spacing: 2px; color: #00E5C4;">{title}</p>'
        f'</td>'
        f'</tr>'
        f'<tr><td colspan="2" height="14" style="font-size: 1px; line-height: 1px;">&nbsp;</td></tr>'
        f'<tr>'
        f'<td width="3" style="font-size: 1px;">&nbsp;</td>'
        f'<td style="padding-left: 14px;">'
        f'<table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">'
        f'{_bullet_rows(items)}'
        f'</table>'
        f'</td>'
        f'</tr>'
        f'<tr><td colspan="2" height="28" style="font-size: 1px; line-height: 1px;">&nbsp;</td></tr>'
        f'</table>'
    )


def _build_html(data: dict, week: int, date_range: str) -> str:
    sections = (
        _section("Tarefas Realizadas", data.get("tasks", []))
        + _section("Bloqueios", data.get("blockers", []))
        + _section("Pr&oacute;xima Semana", data.get("next_week", []))
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="UTF-8">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<!--[if gte mso 9]><xml>
<o:OfficeDocumentSettings><o:AllowPNG/><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings>
</xml><![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #0D0D0D;" bgcolor="#0D0D0D">

<style>
  /* Gmail reads <style> in <body>. New Outlook also respects this. */
  /* color-scheme:light tells Outlook: "don't touch my colors". */
  [data-ogsc] body       {{ background-color: #0D0D0D !important; }}
  [data-ogsc] table.wrap {{ background-color: #0D0D0D !important; }}
  [data-ogsc] table.card {{ background-color: #1A1A1A !important; }}
  [data-ogsc] td.c-head  {{ background-color: #1A1A1A !important; }}
  [data-ogsc] td.c-body  {{ background-color: #1A1A1A !important; }}
  [data-ogsc] td.c-foot  {{ background-color: #0D0D0D !important; }}
  [data-ogsc] .t-label   {{ color: #6B7280 !important; }}
  [data-ogsc] .t-week    {{ color: #FFFFFF !important; }}
  [data-ogsc] .t-date    {{ color: #9CA3AF !important; }}
  [data-ogsc] .t-teal    {{ color: #00E5C4 !important; }}
  [data-ogsc] .t-body    {{ color: #D1D5DB !important; }}
  [data-ogsc] .t-foot    {{ color: #4B5563 !important; }}
  [data-ogsc] td.div-bar {{ background-color: #2D2D2D !important; }}
  [data-ogsc] td.acc-bar {{ background-color: #00E5C4 !important; }}
</style>

<table class="wrap" width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation"
       bgcolor="#0D0D0D" style="background-color: #0D0D0D;">
  <tr>
    <td align="center" style="padding: 40px 16px;">

      <table class="card" width="560" align="center" cellpadding="0" cellspacing="0" border="0"
             role="presentation" bgcolor="#1A1A1A"
             style="width: 560px; background-color: #1A1A1A;">

        <!-- ACCENT TOP BAR -->
        <tr>
          <td class="acc-bar" height="4" bgcolor="#00E5C4"
              style="background-color: #00E5C4; font-size: 1px; line-height: 1px; padding: 0;">&nbsp;</td>
        </tr>

        <!-- HEADER -->
        <tr>
          <td class="c-head" bgcolor="#1A1A1A"
              style="background-color: #1A1A1A; padding: 36px 40px 28px 40px;">
            <p class="t-label"
               style="margin: 0; mso-margin-top-alt: 0; mso-margin-bottom-alt: 0;
                      font-family: Arial, sans-serif; font-size: 10px; font-weight: 700;
                      text-transform: uppercase; letter-spacing: 2.5px; color: #6B7280;
                      mso-line-height-rule: exactly;">Relat&oacute;rio Semanal</p>
            <p class="t-week"
               style="margin: 10px 0 0 0; mso-margin-top-alt: 10px; mso-margin-bottom-alt: 0;
                      font-family: Arial, sans-serif; font-size: 28px; font-weight: 700;
                      color: #FFFFFF; line-height: 1.2; mso-line-height-rule: exactly;">Semana {week}</p>
            <p class="t-date"
               style="margin: 6px 0 0 0; mso-margin-top-alt: 6px; mso-margin-bottom-alt: 0;
                      font-family: Arial, sans-serif; font-size: 14px; color: #9CA3AF;
                      mso-line-height-rule: exactly;">{date_range}</p>
          </td>
        </tr>

        <!-- DIVIDER -->
        <tr>
          <td class="div-bar" height="1" bgcolor="#2D2D2D"
              style="background-color: #2D2D2D; font-size: 1px; line-height: 1px; padding: 0;">&nbsp;</td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td class="c-body" bgcolor="#1A1A1A"
              style="background-color: #1A1A1A; padding: 32px 40px 8px 40px;">
            {sections}
          </td>
        </tr>

        <!-- DIVIDER -->
        <tr>
          <td class="div-bar" height="1" bgcolor="#2D2D2D"
              style="background-color: #2D2D2D; font-size: 1px; line-height: 1px; padding: 0;">&nbsp;</td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td class="c-foot" bgcolor="#0D0D0D"
              style="background-color: #0D0D0D; padding: 18px 40px;">
            <p class="t-foot"
               style="margin: 0; mso-margin-top-alt: 0; mso-margin-bottom-alt: 0;
                      font-family: Arial, sans-serif; font-size: 11px; color: #4B5563;">
              P+Solution Research &nbsp;&middot;&nbsp; Engenharia de Dados &amp; IA
            </p>
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
