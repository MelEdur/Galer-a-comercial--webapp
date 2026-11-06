"""Rebuild the assistant knowledge index.

Run from ``backend/`` (or the Docker container)::

    python -m scripts.reindex_assistant
    python -m scripts.reindex_assistant --store-id 5

The full run rebuilds the static guide and every active store. The per-store
run only replaces that store's document.
"""

from __future__ import annotations

import argparse
import time

import app.db.registry  # noqa: F401  (registers every ORM model)
from app.modules.assistant.indexing import reindex_all, reindex_store


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reindexa la base de conocimiento del asistente."
    )
    parser.add_argument(
        "--store-id",
        type=int,
        default=None,
        help="Reindexa solo el local indicado.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    started = time.perf_counter()

    if args.store_id is not None:
        indexed = reindex_store(args.store_id)
        if indexed:
            print(f"Local {args.store_id}: documento reindexado.")
        else:
            print(
                f"Local {args.store_id}: no existe o está inactivo; "
                "se eliminó su documento previo si existía."
            )
    else:
        result = reindex_all()
        print(
            "Reindexación completa: "
            f"{result.static_chunks} fragmentos estáticos, "
            f"{result.stores_indexed} locales activos y "
            f"{result.store_chunks} fragmentos de locales "
            f"({result.total_chunks} en total)."
        )

    print(f"Tiempo: {time.perf_counter() - started:.1f} s")


if __name__ == "__main__":
    main()
