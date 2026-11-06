"""Intent classification for the public assistant."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Sequence

from app.modules.assistant import llm
from app.modules.assistant.schemas import ChatMessage

logger = logging.getLogger(__name__)

INFORMATIONAL = "informational"
PRODUCT_SEARCH = "product_search"
MAP = "map"
OUT_OF_SCOPE = "out_of_scope"

ALLOWED_INTENTS = (INFORMATIONAL, PRODUCT_SEARCH, MAP, OUT_OF_SCOPE)

INTENT_SYSTEM_PROMPT = """Eres un clasificador de consultas de una galería comercial.
Clasifica la última pregunta del visitante en una de estas intenciones:

- "informational": pregunta sobre la galería, sus locales, categorías, horarios, contacto o información general, o pide ayuda sobre CÓMO USAR la aplicación (por ejemplo, "¿cómo puedo encontrar un local?", "¿cómo funciona el buscador?", "¿cómo veo las ofertas?").
- "product_search": quiere encontrar un producto concreto, conocer precios, stock o qué local vende un artículo.
- "map": quiere ubicar un local concreto dentro de la galería, pregunta dónde está un local o cómo llegar a él.
- "out_of_scope": la consulta no tiene relación con la galería ni con la aplicación.

No uses "map" para preguntas generales sobre cómo usar la aplicación o cómo encontrar locales; usa "map" solo cuando la persona quiera ubicar un local concreto.

Devuelve SOLO un objeto JSON válido, sin explicaciones ni bloques de código, con esta forma:
{"intent": "informational|product_search|map|out_of_scope", "search_query": "texto o null"}

Usa "search_query" solo para "product_search": el término breve que conviene buscar.
Para las demás intenciones devuelve null."""


@dataclass(frozen=True)
class Intent:
    """The classified intention of a visitor message."""

    name: str
    search_query: str | None = None


def history_as_text(history: Sequence[ChatMessage]) -> str:
    """Render previous messages for inclusion in a prompt."""
    if not history:
        return "(sin historial previo)"
    lines: list[str] = []
    for message in history:
        role = "Visitante" if message.role == "user" else "Asistente"
        lines.append(f"{role}: {message.content}")
    return "\n".join(lines)


def _extract_json(raw: str) -> str:
    """Extract the first JSON object from a model response."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end < start:
        raise ValueError("No hay un objeto JSON en la respuesta.")
    return text[start : end + 1]


def parse_intent(raw: str, message: str) -> Intent:
    """Parse the classifier response, falling back to informational."""
    try:
        data = json.loads(_extract_json(raw))
    except (ValueError, TypeError):
        logger.warning("El clasificador no devolvió JSON válido.")
        return Intent(INFORMATIONAL)

    if not isinstance(data, dict):
        return Intent(INFORMATIONAL)

    name = data.get("intent")
    if name not in ALLOWED_INTENTS:
        return Intent(INFORMATIONAL)

    query = data.get("search_query")
    if not isinstance(query, str) or not query.strip():
        query = None
    else:
        query = query.strip()

    if name == PRODUCT_SEARCH and query is None:
        query = message.strip() or None

    return Intent(name=name, search_query=query)


def classify(message: str, history: Sequence[ChatMessage]) -> Intent:
    """Ask the chat model for the intention behind ``message``."""
    raw = llm.generate(
        [
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Historial de la conversación:\n"
                    f"{history_as_text(history)}\n\n"
                    f"Última pregunta del visitante: {message}"
                ),
            },
        ]
    )
    return parse_intent(raw, message)
