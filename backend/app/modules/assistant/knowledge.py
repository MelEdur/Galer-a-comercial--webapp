"""Static and per-store knowledge documents for the assistant index.

The static guide is split into overlapping chunks. Each active store produces a
single descriptive chunk with its public data and commercial categories. Store
products, prices and stock are deliberately excluded from the index.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATIC_SOURCE_ID = "galeria"
STATIC_TITLE = "Guía de la galería"

KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"
STATIC_PATH = KNOWLEDGE_DIR / "galeria.md"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNK_SEPARATORS = ["\n## ", "\n### ", "\n", ". ", " "]

_DAY_NAMES = (
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
)

_SIDE_NAMES = {
    "left": "izquierdo",
    "right": "derecho",
    "back": "fondo",
}


@dataclass(frozen=True)
class KnowledgeChunk:
    """A text fragment ready to be embedded and stored in ChromaDB."""

    id: str
    text: str
    metadata: dict[str, Any]


def _splitter() -> Any:
    """Build the recursive splitter used for the static guide."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=CHUNK_SEPARATORS,
    )


def _file_updated_at(path: Path) -> str:
    """Return the file modification time as an ISO timestamp."""
    try:
        return datetime.fromtimestamp(
            path.stat().st_mtime, tz=timezone.utc
        ).isoformat()
    except OSError:
        return ""


def static_chunks(path: Path | None = None) -> list[KnowledgeChunk]:
    """Split the static Markdown guide into deterministic chunks."""
    source_path = path or STATIC_PATH
    text = source_path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    updated_at = _file_updated_at(source_path)
    pieces = _splitter().split_text(text)

    return [
        KnowledgeChunk(
            id=f"static:{STATIC_SOURCE_ID}:{index}",
            text=piece,
            metadata={
                "source_type": "static",
                "source_id": STATIC_SOURCE_ID,
                "title": STATIC_TITLE,
                "updated_at": updated_at,
            },
        )
        for index, piece in enumerate(pieces)
        if piece.strip()
    ]


def _store_categories(store: Any) -> list[str]:
    """Return the distinct categories of the store's available products."""
    names: set[str] = set()
    for product in getattr(store, "products", []) or []:
        if getattr(product, "deleted_at", None) is not None:
            continue
        if not getattr(product, "is_active", True):
            continue
        for link in getattr(product, "product_categories", []) or []:
            category = getattr(link, "category", None)
            name = getattr(category, "name", None)
            if name:
                names.add(name)
    return sorted(names, key=str.lower)


def _hours_text(store: Any) -> str:
    """Format the published opening intervals grouped by weekday."""
    grouped: dict[int, list[tuple[str, str]]] = {}
    for hour in getattr(store, "hours", []) or []:
        day = int(hour.day_of_week)
        grouped.setdefault(day, []).append(
            (hour.opens_at.strftime("%H:%M"), hour.closes_at.strftime("%H:%M"))
        )

    lines: list[str] = []
    for day in sorted(grouped):
        name = _DAY_NAMES[day] if 0 <= day < len(_DAY_NAMES) else f"Día {day}"
        intervals = ", ".join(
            f"{opens} a {closes}"
            for opens, closes in sorted(grouped[day])
        )
        lines.append(f"- {name}: {intervals}")
    return "\n".join(lines)


def _links_text(store: Any) -> str:
    """Format the store's external links in their published order."""
    links = sorted(
        getattr(store, "links", []) or [],
        key=lambda link: getattr(link, "position", 0),
    )
    return "\n".join(
        f"- {link.label}: {link.url}"
        for link in links
        if getattr(link, "url", None)
    )


def _contact_text(store: Any) -> str:
    """Format the contact channels the store chose to publish."""
    lines: list[str] = []
    if getattr(store, "phone", None):
        lines.append(f"- Teléfono: {store.phone}")
    if getattr(store, "whatsapp", None):
        lines.append(f"- WhatsApp: {store.whatsapp}")
    if getattr(store, "email", None):
        lines.append(f"- Correo electrónico: {store.email}")
    return "\n".join(lines)


def store_chunk(store: Any) -> KnowledgeChunk:
    """Build the single knowledge chunk that describes one store."""
    title = f"Local {store.number} — {store.name}"
    lines = [f"## {title}"]

    if getattr(store, "description", None):
        lines.append(store.description.strip())

    lines.append(f"Número de local: {store.number}.")
    side = _SIDE_NAMES.get(store.side, store.side)
    lines.append(
        f"Ubicación en el mapa: lado {side}, posición {store.position}."
    )

    categories = _store_categories(store)
    if categories:
        lines.append(
            "Categorías comerciales: " + ", ".join(categories) + "."
        )

    contact = _contact_text(store)
    lines.append("Contacto publicado:")
    lines.append(contact or "- La aplicación no publica datos de contacto de este local.")

    hours = _hours_text(store)
    lines.append("Horarios publicados:")
    lines.append(hours or "- La aplicación no publica horarios de este local.")

    links = _links_text(store)
    lines.append("Enlaces publicados:")
    lines.append(links or "- La aplicación no publica enlaces de este local.")

    updated_at = ""
    timestamp = getattr(store, "updated_at", None)
    if timestamp is not None:
        updated_at = timestamp.isoformat()

    return KnowledgeChunk(
        id=f"store:{store.id}:0",
        text="\n".join(lines),
        metadata={
            "source_type": "store",
            "source_id": f"store:{store.id}",
            "title": title,
            "store_id": int(store.id),
            "updated_at": updated_at,
        },
    )
