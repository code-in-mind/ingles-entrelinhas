"""
Lê cartoes/*.yml (a FONTE ÚNICA dos flashcards) e gera, para cada módulo,
a página docs/modulos/<modulo>/flashcards.md com os cartões viráveis.

O mesmo YAML alimenta três saídas diferentes:
  - esta página do site      (scripts/build_flashcards.py)
  - o baralho do Anki .apkg  (scripts/export_anki.py)
  - a tabela do livro        (scripts/build_book.py)

Nunca escreva um flashcard direto no Markdown: escreva no YAML.
"""

from __future__ import annotations

import html
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
CARTOES = RAIZ / "cartoes"
MODULOS = RAIZ / "docs" / "modulos"

CABECALHO = """---
title: Flashcards — {titulo}
tags: [flashcards, {nivel}]
---

# Flashcards — {titulo}

!!! tip "Como usar"
    Clique no cartão (ou tecle ++enter++ com ele focado) para virar.
    Para revisão espaçada de verdade, baixe o baralho e use o Anki:
    `poetry run python scripts/export_anki.py`

<div class="flashcards" markdown="0">
"""

CARTAO = """  <div class="flashcard" tabindex="0" role="button" aria-label="Virar cartão">
    <div class="flashcard__face flashcard__front">{frente}</div>
    <div class="flashcard__face flashcard__back">
      <strong>{verso}</strong>{exemplo}
    </div>
  </div>
"""


def gerar_um(caminho_yml: Path) -> Path:
    dados = yaml.safe_load(caminho_yml.read_text(encoding="utf-8"))
    modulo = dados["modulo"]
    destino = MODULOS / modulo / "flashcards.md"
    destino.parent.mkdir(parents=True, exist_ok=True)

    partes = [CABECALHO.format(titulo=dados["titulo"], nivel=dados.get("nivel", "A1"))]

    for cartao in dados["cartoes"]:
        exemplo = cartao.get("exemplo", "")
        exemplo_html = f"<br><em>{html.escape(exemplo)}</em>" if exemplo else ""
        partes.append(
            CARTAO.format(
                frente=html.escape(str(cartao["frente"])),
                verso=html.escape(str(cartao["verso"])),
                exemplo=exemplo_html,
            )
        )

    partes.append("</div>\n")

    # Lista de origem: liga cada cartão à nota que o originou.
    com_nota = [c for c in dados["cartoes"] if c.get("nota")]
    if com_nota:
        partes.append("\n## De onde vieram estes cartões\n\n")
        vistos = []
        for cartao in com_nota:
            if cartao["nota"] not in vistos:
                vistos.append(cartao["nota"])
        for nota_id in vistos:
            partes.append(f"- [[{nota_id}]]\n")

    destino.write_text("".join(partes), encoding="utf-8")
    return destino


def main() -> None:
    arquivos = sorted(CARTOES.glob("*.yml"))
    if not arquivos:
        print("Nenhum YAML em cartoes/. Nada a fazer.")
        return
    for arquivo in arquivos:
        destino = gerar_um(arquivo)
        print(f"{arquivo.name} -> {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
