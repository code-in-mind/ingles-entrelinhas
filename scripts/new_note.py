"""
Cria um zettel novo já com ID, front matter e esqueleto.

    poetry run python scripts/new_note.py "Present Perfect vs Past Simple" \
        --tags gramatica tempos-verbais B1 \
        --source "Aula X — youtu.be/abc123 (12:40)"

O ID é o carimbo de tempo AAAAMMDDHHMM. Ele nunca muda, mesmo que o
título mude depois — é isso que mantém os [[links]] válidos para sempre.
"""

import argparse
import re
import unicodedata
from datetime import datetime
from pathlib import Path

NOTAS = Path(__file__).resolve().parent.parent / "docs" / "notas"

MODELO = """---
title: {titulo}
tags: {tags}
nivel: {nivel}
fonte: "{fonte}"
criada: {data}
---

# {titulo}

<!-- Uma ideia só, escrita com as suas palavras, em 3 a 8 linhas. -->

## Exemplos

> 

## Conexões

<!-- Cole aqui os IDs das notas relacionadas: [[202609161430]] -->

"""


def slug(texto: str) -> str:
    """'Present Perfect vs Past Simple' -> 'present-perfect-vs-past-simple'"""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    return re.sub(r"[\s_]+", "-", texto)


def main() -> None:
    p = argparse.ArgumentParser(description="Cria um zettel novo.")
    p.add_argument("titulo")
    p.add_argument("--tags", nargs="*", default=[])
    p.add_argument("--level", default="A1", help="A1, A2, B1, B2 ou C1")
    p.add_argument("--source", default="")
    args = p.parse_args()

    agora = datetime.now()
    nota_id = agora.strftime("%Y%m%d%H%M")
    caminho = NOTAS / f"{nota_id}-{slug(args.titulo)}.md"
    NOTAS.mkdir(parents=True, exist_ok=True)

    caminho.write_text(
        MODELO.format(
            titulo=args.titulo,
            tags="[" + ", ".join(args.tags) + "]",
            nivel=args.level,
            fonte=args.source,
            data=agora.strftime("%Y-%m-%d"),
        ),
        encoding="utf-8",
    )
    print(f"Criada: {caminho.relative_to(caminho.parent.parent.parent)}")
    print(f"ID para citar em outras notas: [[{nota_id}]]")


if __name__ == "__main__":
    main()
