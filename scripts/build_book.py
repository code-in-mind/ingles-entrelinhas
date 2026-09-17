"""
Monta o manuscrito do livro a partir do MESMO Markdown que gera o site.

    poetry run python scripts/build_book.py            # só o .md
    poetry run python scripts/build_book.py --epub     # + EPUB via pandoc
    poetry run python scripts/build_book.py --pdf      # + PDF via pandoc

O que ele faz, na ordem:

1. Lê a ordem dos módulos direto do `nav` do mkdocs.yml.
   Assim o sumário do livro e o do site NUNCA divergem.
2. Junta os capítulos num único arquivo.
3. Adapta o que só funciona na tela:
   - [[wikilink]]        -> referência cruzada interna do livro
   - <audio>             -> link do episódio no YouTube
   - cartões viráveis     -> tabela de duas colunas (relida do YAML)
   - ??? "Resposta"       -> gabarito no fim do capítulo
4. Anexa o caderno de notas (os zettels) como apêndice, com âncoras,
   para que as referências cruzadas tenham destino.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
SAIDA = RAIZ / "livro" / "saida"

# Nome do projeto lido de config/site.yml — nunca hardcoded aqui, então
# renomear o projeto não exige tocar neste arquivo.
NOME_PROJETO = yaml.safe_load(
    (RAIZ / "config" / "site.yml").read_text(encoding="utf-8")
)["name"]

WIKILINK = re.compile(r"\[\[(\d{12})(?:\|([^\]]+))?\]\]")
BLOCO_HTML = re.compile(r"<div class=\"flashcards\".*?</div>\s*$", re.S | re.M)
AUDIO = re.compile(r"<audio[^>]*>.*?</audio>", re.S)
RESPOSTA = re.compile(r'^\?\?\?\+? +\w+ +"Resposta"\n((?:(?: {4}.*)?\n)+)', re.M)
# !!! note "Título" seguido do corpo indentado em 4 espaços
ADMONITION = re.compile(r'^(?:!!!|\?\?\?)\+? +\w+(?: +"([^"]*)")?\n((?:(?: {4}.*)?\n)+)', re.M)
# === "Rótulo" (pymdownx.tabbed) seguido do corpo indentado em 4 espaços
ABA = re.compile(r'^=== +"([^"]*)"\n((?:(?: {4}.*)?\n)+)', re.M)


# ---------------------------------------------------------------- utilidades

def front_matter(texto: str) -> tuple[dict, str]:
    """Separa o YAML do topo do corpo do texto."""
    if texto.startswith("---"):
        partes = texto.split("---", 2)
        if len(partes) >= 3:
            return (yaml.safe_load(partes[1]) or {}), partes[2].lstrip("\n")
    return {}, texto


def indice_notas() -> dict[str, dict]:
    """id -> {titulo, corpo} de todos os zettels."""
    indice = {}
    for arquivo in sorted((DOCS / "notas").glob("*.md")):
        m = re.match(r"^(\d{12})", arquivo.name)
        if not m:
            continue
        fm, corpo = front_matter(arquivo.read_text(encoding="utf-8"))
        indice[m.group(1)] = {
            "titulo": fm.get("title", arquivo.stem),
            "corpo": corpo,
            "nivel": fm.get("nivel", ""),
        }
    return indice


def ordem_dos_capitulos() -> list[Path]:
    """Extrai de mkdocs.yml, na ordem do nav, todos os .md sob modulos/."""
    bruto = (RAIZ / "mkdocs.yml").read_text(encoding="utf-8")
    # O mkdocs.yml usa tags do Material que o yaml puro não entende;
    # por isso varremos o nav por regex em vez de fazer yaml.safe_load.
    dentro_nav = bruto.split("\nnav:", 1)[1]
    caminhos = re.findall(r"([\w./-]+\.md)", dentro_nav)
    vistos, ordenados = set(), []
    for c in caminhos:
        # modulos/index.md é navegação do site, não capítulo do livro.
        if c == "modulos/index.md":
            continue
        if c.startswith("modulos/") and c not in vistos:
            vistos.add(c)
            ordenados.append(DOCS / c)
    return [p for p in ordenados if p.exists()]


# ------------------------------------------------------------ transformações

def tabela_flashcards(caminho_md: Path) -> str:
    """No livro, cartão virado não existe: vira tabela. Relê o YAML de origem."""
    modulo = caminho_md.parent.name
    yml = RAIZ / "cartoes" / f"{modulo}.yml"
    if not yml.exists():
        return ""
    dados = yaml.safe_load(yml.read_text(encoding="utf-8"))
    linhas = ["", "| Pergunta | Resposta |", "| --- | --- |"]
    for c in dados["cartoes"]:
        exemplo = f" — *{c['exemplo']}*" if c.get("exemplo") else ""
        linhas.append(f"| {c['frente']} | **{c['verso']}**{exemplo} |")
    linhas.append("")
    return "\n".join(linhas)


def extrair_gabarito(corpo: str, prefixo: str) -> tuple[str, list[str]]:
    """Tira as respostas do meio do exercício e guarda para o fim do capítulo."""
    respostas: list[str] = []

    def troca(m: re.Match) -> str:
        texto = "\n".join(l[4:] for l in m.group(1).splitlines() if l.strip())
        respostas.append(texto)
        return f"*(gabarito {prefixo}.{len(respostas)})*\n\n"

    return RESPOSTA.sub(troca, corpo), respostas


def adaptar(corpo: str, notas: dict, caminho: Path, prefixo: str) -> tuple[str, list[str]]:
    # 1. Cartões viráveis -> tabela
    if caminho.name == "flashcards.md":
        corpo = BLOCO_HTML.sub(tabela_flashcards(caminho), corpo)

    # 2. Áudio -> link do episódio
    corpo = AUDIO.sub(
        f"> :material-headphones: **Ouça este episódio** no canal *{NOME_PROJETO}* "
        "no YouTube (o link está na página do módulo no site).",
        corpo,
    )

    # 3. Wikilinks -> referência cruzada interna
    def link(m: re.Match) -> str:
        nota = notas.get(m.group(1))
        if not nota:
            return ""
        texto = m.group(2) or nota["titulo"]
        return f"[{texto}](#nota-{m.group(1)})"

    corpo = WIKILINK.sub(link, corpo)

    # 3b. Links entre páginas do site (.md) não existem no livro:
    #     viram o próprio texto em itálico.
    corpo = re.sub(r"\[([^\]]+)\]\((?!https?:)[^)]*\.md[^)]*\)", r"*\1*", corpo)

    # 3c. A seção "Continue" é navegação do site; no livro a página seguinte
    #     já é a página seguinte.
    corpo = re.sub(r"\n## Continue\n.*?(?=\n## |\Z)", "\n", corpo, flags=re.S)

    # 4. Gabarito para o fim
    corpo, respostas = extrair_gabarito(corpo, prefixo)

    # 5. Admonitions do Material -> citação (pandoc não conhece a sintaxe '!!!').
    #    Precisa remover a indentação de 4 espaços do corpo, senão o pandoc
    #    interpreta o bloco inteiro como código.
    def admoestacao(m: re.Match) -> str:
        titulo, corpo_adm = m.group(1), m.group(2)
        linhas = ["> **" + titulo + "**", ">"] if titulo else []
        for linha in corpo_adm.splitlines():
            linhas.append("> " + linha[4:] if linha.strip() else ">")
        return "\n".join(linhas) + "\n\n"

    corpo = ADMONITION.sub(admoestacao, corpo)

    # 5b. Abas (pymdownx.tabbed) -> cada aba vira uma seção com o rótulo em
    #     negrito. No livro não existe clique para trocar de aba, então as
    #     opções aparecem uma após a outra, em sequência de leitura.
    def desdobrar_aba(m: re.Match) -> str:
        rotulo, corpo_aba = m.group(1), m.group(2)
        linhas = ["**" + rotulo + "**", ""]
        for linha in corpo_aba.splitlines():
            linhas.append(linha[4:] if linha.strip() else "")
        return "\n".join(linhas) + "\n\n"

    corpo = ABA.sub(desdobrar_aba, corpo)

    return corpo, respostas


# ------------------------------------------------------------------ montagem

def montar() -> Path:
    notas = indice_notas()
    capitulos = ordem_dos_capitulos()
    pedacos: list[str] = []

    modulo_atual = None
    for caminho in capitulos:
        fm, corpo = front_matter(caminho.read_text(encoding="utf-8"))
        modulo = caminho.parent.name

        if modulo != modulo_atual:
            modulo_atual = modulo
            pedacos.append(f"\n\n# {fm.get('title', modulo)}\n")
            corpo = re.sub(r"^# .*\n", "", corpo, count=1)
        else:
            # Subpáginas (exercícios, flashcards) viram seções do capítulo:
            # todos os títulos descem um nível para não competir com o capítulo.
            corpo = re.sub(r"^(#{1,4}) ",
                           lambda m: "#" * (len(m.group(1)) + 1) + " ",
                           corpo, flags=re.M)

        adaptado, respostas = adaptar(corpo, notas, caminho, modulo[:2])
        pedacos.append(adaptado)

        if respostas:
            pedacos.append(f"\n### Gabarito\n\n")
            for i, r in enumerate(respostas, 1):
                pedacos.append(f"**{modulo[:2]}.{i}** {r}\n\n")

    # Apêndice: o caderno de notas, com âncoras para as referências cruzadas.
    pedacos.append("\n\n# Apêndice — Caderno de notas\n\n")
    pedacos.append(
        "Estas são as notas atômicas que deram origem aos capítulos. "
        "Cada uma trata de uma ideia só e pode ser lida fora de ordem.\n\n"
    )
    for nota_id, nota in sorted(notas.items()):
        corpo = re.sub(r"^# (.*)\n", "", nota["corpo"], count=1)
        corpo = WIKILINK.sub(
            lambda m: f"[{notas[m.group(1)]['titulo']}](#nota-{m.group(1)})"
            if m.group(1) in notas else "", corpo)
        corpo = re.sub(r"^<!--.*?-->\s*$", "", corpo, flags=re.M | re.S)
        pedacos.append(f"## {nota['titulo']} {{#nota-{nota_id}}}\n\n{corpo}\n")

    SAIDA.mkdir(parents=True, exist_ok=True)
    destino = SAIDA / "livro.md"
    destino.write_text("\n".join(pedacos), encoding="utf-8")
    return destino


def pandoc(manuscrito: Path, formato: str) -> None:
    """
    Chama o Pandoc para converter o MESMO manuscrito em um formato de saída.

    Todo formato passa pelo mesmo filtro Lua (livro/filtros/livro.lua), que
    limpa o que só existe na tela (ícones do Material, HTML cru). O que muda
    de um formato para o outro é só o motor de renderização e o visual.
    """
    extensoes = {"epub": ".epub", "pdf": ".pdf", "docx": ".docx"}
    saida = manuscrito.with_suffix(extensoes[formato])
    comando = [
        "pandoc",
        str(RAIZ / "livro" / "metadata.yaml"),
        str(manuscrito),
        "--from", "markdown+pipe_tables+header_attributes",
        "--toc", "--toc-depth=2",
        "--top-level-division=chapter",
        "--lua-filter", str(RAIZ / "livro" / "filtros" / "livro.lua"),
        "-o", str(saida),
    ]

    if formato == "epub":
        # Formato principal de venda: Kindle (KDP aceita EPUB desde 2022),
        # Google Play Books, Apple Books, Kobo.
        comando += ["--css", str(RAIZ / "livro" / "epub.css")]

    elif formato == "pdf":
        # Formato de impressão sob demanda / venda direta em PDF.
        comando += ["--pdf-engine=xelatex", "-V", "mainfont=DejaVu Serif",
                    "-V", "geometry:margin=2.5cm", "-V", "fontsize=11pt",
                    "-V", "linestretch=1.15"]

    elif formato == "docx":
        # Não é para venda — é para revisão humana: mandar para um editor,
        # revisor ou diagramador que não mexe com Markdown/Git. Usa um
        # modelo de referência (livro/referencia.docx) para herdar estilos
        # de título e corpo em vez do padrão genérico do Pandoc.
        referencia = RAIZ / "livro" / "referencia.docx"
        if referencia.exists():
            comando += ["--reference-doc", str(referencia)]

    subprocess.run(comando, check=True)
    print(f"-> {saida.relative_to(RAIZ)}")


def main() -> None:
    p = argparse.ArgumentParser(description="Monta o livro a partir do site.")
    p.add_argument("--epub", action="store_true", help="gera o .epub (venda)")
    p.add_argument("--pdf", action="store_true", help="gera o .pdf (venda/impressão)")
    p.add_argument("--docx", action="store_true", help="gera o .docx (revisão humana)")
    p.add_argument("--all", action="store_true", help="gera epub + pdf + docx")
    args = p.parse_args()

    manuscrito = montar()
    palavras = len(manuscrito.read_text(encoding="utf-8").split())
    print(f"Manuscrito: {manuscrito.relative_to(RAIZ)} ({palavras} palavras)")

    formatos = []
    if args.all:
        formatos = ["epub", "pdf", "docx"]
    else:
        if args.epub:
            formatos.append("epub")
        if args.pdf:
            formatos.append("pdf")
        if args.docx:
            formatos.append("docx")

    if not formatos:
        print("Nenhum formato pedido — use --epub, --pdf, --docx ou --all.")
        return

    for formato in formatos:
        pandoc(manuscrito, formato)


if __name__ == "__main__":
    main()
