import logging
from openai import OpenAI
import config

logger = logging.getLogger(__name__)

_client = OpenAI(api_key=config.OPENAI_API_KEY)

SYSTEM_PROMPT = """Você é um assistente especializado em formatação de relatórios corporativos para engenheiros de dados e IA.

Sua tarefa é transformar notas brutas em um relatório semanal formal e bem estruturado.

Regras:
- Tom formal e corporativo, mas direto
- Preserve todas as métricas, números e dados mencionados
- Organize em seções nesta ordem quando houver conteúdo: Engenharia de Dados, IA & Modelos, Estudos, Reuniões, Bloqueios, Próxima Semana
- Omita completamente seções sem conteúdo
- Retorne apenas o corpo do e-mail — sem saudação, sem assinatura, sem cabeçalho
- Use bullet points com hífen para listar itens dentro de cada seção
- Mantenha cada seção com um título em negrito seguido de dois pontos"""


def format_report(raw_content: str) -> str:
    logger.info("Sending content to GPT-4o for formatting")

    response = _client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Formate o seguinte relatório semanal:\n\n{raw_content}"},
        ],
    )

    formatted = response.choices[0].message.content.strip()
    logger.info(f"Formatting complete ({len(formatted)} chars)")
    return formatted
