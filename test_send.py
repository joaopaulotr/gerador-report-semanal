"""
Test script: builds HTML with fake data and sends email — no GPT call.
Run: python test_send.py
"""
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from src.formatter import _build_html, _current_week_info
from src.sender import send_report

FAKE_DATA = {
    "tasks": [
        "Desenvolvimento de processo ETL para extração e carga de 600 mil registros a partir de 340 planilhas.",
        "Implementação de ETL para dados de surveys, resultando em 100 mil novos registros.",
        "Atualização completa da documentação do banco de dados.",
        "Refatoração do processo de leitura de cédulas, reduzindo em 42% o custo com a API do ChatGPT.",
    ],
    "blockers": [],
    "next_week": [
        "Remover opt-in do banco de dados dentro da Pesquise Mais Solutions.",
        "Consolidar banco de dados do Cédula Reader.",
    ],
}

if __name__ == "__main__":
    week, date_range = _current_week_info()
    html = _build_html(FAKE_DATA, week, date_range)
    send_report(html)
    print("Done — check inbox.")
