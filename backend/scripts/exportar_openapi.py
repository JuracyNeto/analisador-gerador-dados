"""Grava o schema OpenAPI em JSON para gerar os tipos do frontend (D34)."""

import json
import sys
from pathlib import Path

from app.main import create_app

DESTINO_PADRAO = Path("../frontend/openapi.json")


def main() -> None:
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else DESTINO_PADRAO
    schema = create_app().openapi()
    destino.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OpenAPI gravado em {destino.resolve()}")


if __name__ == "__main__":
    main()
