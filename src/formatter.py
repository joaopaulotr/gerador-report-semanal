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
            f'<td width="20" valign="top" style="font-family: Arial, sans-serif; font-size: 16px; line-height: 22px; color: #00C9A7; padding: 0 0 10px 0; mso-line-height-rule: exactly;">&#8250;</td>'
            f'<td valign="top" style="font-family: Arial, sans-serif; font-size: 14px; line-height: 22px; color: #a1a1aa; padding: 0 0 10px 0; mso-line-height-rule: exactly;">{item}</td>'
            f'</tr>'
        )
    return "".join(rows)


def _section(title: str, items: list) -> str:
    if not items:
        return ""
    return (
        f'<table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">'
        # left accent bar + title row
        f'<tr>'
        f'<td width="3" bgcolor="#00C9A7" style="background-color: #00C9A7; font-size: 1px; line-height: 1px; border-radius: 2px;">&nbsp;</td>'
        f'<td style="padding: 0 0 0 12px;">'
        f'<p style="margin: 0; mso-margin-top-alt: 0; mso-margin-bottom-alt: 0; font-family: Arial, sans-serif; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.8px; color: #00C9A7;">{title}</p>'
        f'</td>'
        f'</tr>'
        # spacer
        f'<tr><td colspan="2" height="14" style="font-size: 1px; line-height: 1px;">&nbsp;</td></tr>'
        # bullet rows (indented to align with title text)
        f'<tr>'
        f'<td width="3" style="font-size: 1px;">&nbsp;</td>'
        f'<td style="padding-left: 12px;">'
        f'<table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">'
        f'{_bullet_rows(items)}'
        f'</table>'
        f'</td>'
        f'</tr>'
        # bottom spacer
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
<meta name="color-scheme" content="dark">
<meta name="supported-color-schemes" content="dark">
<!--[if gte mso 9]><xml>
<o:OfficeDocumentSettings><o:AllowPNG/><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings>
</xml><![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #09090b;" bgcolor="#09090b">

<table width="100%" bgcolor="#09090b" cellpadding="0" cellspacing="0" border="0" role="presentation">
  <tr>
    <td align="center" style="padding: 40px 16px;">

      <!-- outer card -->
      <table width="560" align="center" cellpadding="0" cellspacing="0" border="0" role="presentation"
             style="width: 560px; background-color: #18181b; border: 1px solid #27272a;"
             bgcolor="#18181b">

        <!-- ACCENT BAR top -->
        <tr>
          <td height="4" bgcolor="#00C9A7"
              style="background-color: #00C9A7; font-size: 1px; line-height: 1px; padding: 0;">&nbsp;</td>
        </tr>

        <!-- HEADER -->
        <tr>
          <td bgcolor="#18181b" style="background-color: #18181b; padding: 36px 40px 28px 40px;">
            <p style="margin: 0; mso-margin-top-alt: 0; mso-margin-bottom-alt: 0;
                      font-family: Arial, sans-serif; font-size: 10px; font-weight: 700;
                      text-transform: uppercase; letter-spacing: 2.5px; color: #52525b;
                      mso-line-height-rule: exactly;">Relat&oacute;rio Semanal</p>
            <p style="margin: 10px 0 0 0; mso-margin-top-alt: 10px; mso-margin-bottom-alt: 0;
                      font-family: Arial, sans-serif; font-size: 26px; font-weight: 700;
                      color: #fafafa; mso-line-height-rule: exactly; line-height: 1.2;">
              Semana {week}
            </p>
            <p style="margin: 4px 0 0 0; mso-margin-top-alt: 4px; mso-margin-bottom-alt: 0;
                      font-family: Arial, sans-serif; font-size: 14px; font-weight: 400;
                      color: #71717a; mso-line-height-rule: exactly;">{date_range}</p>
          </td>
        </tr>

        <!-- HEADER DIVIDER -->
        <tr>
          <td height="1" bgcolor="#27272a"
              style="background-color: #27272a; font-size: 1px; line-height: 1px; padding: 0;">&nbsp;</td>
        </tr>

        <!-- CONTENT -->
        <tr>
          <td bgcolor="#18181b" style="background-color: #18181b; padding: 32px 40px 8px 40px;">
            {sections}
          </td>
        </tr>

        <!-- FOOTER DIVIDER -->
        <tr>
          <td height="1" bgcolor="#27272a"
              style="background-color: #27272a; font-size: 1px; line-height: 1px; padding: 0;">&nbsp;</td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td bgcolor="#09090b" style="background-color: #09090b; padding: 18px 40px;">
            <p style="margin: 0; mso-margin-top-alt: 0; mso-margin-bottom-alt: 0;
                      font-family: Arial, sans-serif; font-size: 11px; color: #3f3f46;">
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
