"""
Exporta cartoes/*.yml para um baralho .apkg do Anki.

    poetry run python scripts/export_anki.py
    # gera livro/saida/<nome-do-projeto-em-slug>.apkg

Por que Anki e não só o site: repetição espaçada precisa de agendamento,
e agendamento precisa de estado por aluno. Um site estático não guarda isso.
O site serve para folhear; o Anki serve para memorizar.
"""

from __future__ import annotations

import random
import re
import unicodedata
from pathlib import Path

import genanki
import yaml

RAIZ = Path(__file__).resolve().parent.parent
CARTOES = RAIZ / "cartoes"
SAIDA = RAIZ / "livro" / "saida"

# Nome do projeto lido de config/site.yml — nunca hardcoded aqui, então
# renomear o projeto não exige tocar neste arquivo.
NOME_PROJETO = yaml.safe_load(
    (RAIZ / "config" / "site.yml").read_text(encoding="utf-8")
)["name"]

# IDs fixos: se mudarem entre exportações, o Anki trata como baralho novo
# e o aluno perde o histórico de revisões. Não altere depois de publicar.
ID_MODELO = 1607392319
ID_BARALHO_BASE = 2059400110

MODELO = genanki.Model(
    ID_MODELO,
    NOME_PROJETO,
    fields=[{"name": "Frente"}, {"name": "Verso"}, {"name": "Exemplo"}],
    templates=[
        {
            "name": "Cartão 1",
            "qfmt": '<div class="frente">{{Frente}}</div>',
            "afmt": '{{FrontSide}}<hr id="answer">'
                    '<div class="verso">{{Verso}}</div>'
                    '<div class="exemplo">{{Exemplo}}</div>',
        }
    ],
    css="""
.card { font-family: -apple-system, system-ui, sans-serif;
        font-size: 22px; text-align: center; color: #1b1b1f; background: #fff; }
.verso { font-weight: 700; margin-top: .6em; }
.exemplo { font-size: 16px; font-style: italic; color: #555; margin-top: .6em; }
""",
)


def main() -> None:
    baralhos = []
    total = 0

    for arquivo in sorted(CARTOES.glob("*.yml")):
        dados = yaml.safe_load(arquivo.read_text(encoding="utf-8"))
        nome = f"{NOME_PROJETO}::{dados['nivel']} {dados['titulo']}"
        # ID derivado do nome, para ser estável entre execuções.
        baralho = genanki.Deck(ID_BARALHO_BASE + abs(hash(dados["modulo"])) % 100000, nome)

        for cartao in dados["cartoes"]:
            baralho.add_note(
                genanki.Note(
                    model=MODELO,
                    fields=[
                        str(cartao["frente"]),
                        str(cartao["verso"]),
                        str(cartao.get("exemplo", "")),
                    ],
                    tags=[t.replace(" ", "-") for t in cartao.get("tags", [])],
                )
            )
            total += 1

        baralhos.append(baralho)
        print(f"{arquivo.name}: {len(dados['cartoes'])} cartões")

    if not baralhos:
        print("Nenhum YAML em cartoes/.")
        return

    SAIDA.mkdir(parents=True, exist_ok=True)
    # Sem acento no nome do arquivo — mais portável entre sistemas.
    sem_acento = unicodedata.normalize("NFKD", NOME_PROJETO).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^\w]+", "-", sem_acento.lower()).strip("-")
    destino = SAIDA / f"{slug}.apkg"
    genanki.Package(baralhos).write_to_file(destino)
    print(f"\n{total} cartões em {len(baralhos)} baralhos -> {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
