"""
Hook do MkDocs que dá ao site o comportamento de Zettelkasten.

Faz duas coisas, nesta ordem:

1. Resolve wikilinks  [[202609161430]]  ou  [[202609161430|outro texto]]
   para links Markdown normais, com caminho relativo correto.
2. Monta e injeta a seção de BACKLINKS ("quais notas apontam para esta"),
   que é o que transforma uma pasta de arquivos numa rede de verdade.

O hook roda automaticamente: está declarado em `hooks:` no mkdocs.yml.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

# [[ID]] ou [[ID|texto alternativo]] — o ID é sempre AAAAMMDDHHMM (12 dígitos)
WIKILINK = re.compile(r"\[\[(\d{12})(?:\|([^\]]+))?\]\]")

# Índice global, preenchido em on_files e consumido em on_page_markdown.
INDICE: dict[str, dict] = {}      # id -> {"src": "notas/x.md", "titulo": "..."}
BACKLINKS: dict[str, list] = {}   # id de destino -> [(id de origem, titulo)]


def _front_matter(texto: str) -> dict:
    """Lê o bloco YAML entre '---' no topo do arquivo. Devolve {} se não houver."""
    if not texto.startswith("---"):
        return {}
    partes = texto.split("---", 2)
    if len(partes) < 3:
        return {}
    try:
        return yaml.safe_load(partes[1]) or {}
    except yaml.YAMLError:
        return {}


def _id_do_arquivo(caminho: Path) -> str | None:
    """O ID da nota é o prefixo numérico do nome do arquivo."""
    m = re.match(r"^(\d{12})", caminho.name)
    return m.group(1) if m else None


def on_files(files, config):
    """Varre docs/notas/ uma única vez e monta o índice e os backlinks."""
    INDICE.clear()
    BACKLINKS.clear()

    docs_dir = Path(config["docs_dir"])
    pasta_notas = docs_dir / "notas"
    if not pasta_notas.is_dir():
        return files

    # Primeira passada: quem é quem.
    for arquivo in sorted(pasta_notas.glob("*.md")):
        nota_id = _id_do_arquivo(arquivo)
        if not nota_id:
            continue
        texto = arquivo.read_text(encoding="utf-8")
        fm = _front_matter(texto)
        INDICE[nota_id] = {
            "src": arquivo.relative_to(docs_dir).as_posix(),
            "titulo": fm.get("title") or arquivo.stem,
            "texto": texto,
        }

    # Segunda passada: quem aponta para quem.
    for nota_id, dados in INDICE.items():
        for destino, _rotulo in WIKILINK.findall(dados["texto"]):
            if destino == nota_id:
                continue
            BACKLINKS.setdefault(destino, []).append((nota_id, dados["titulo"]))

    return files


def _rel(de_src: str, para_src: str) -> str:
    """Caminho relativo de uma página para outra, em estilo URL."""
    origem = os.path.dirname(de_src)
    return Path(os.path.relpath(para_src, origem or ".")).as_posix()


def on_page_markdown(markdown, page, config, files):
    src = page.file.src_uri

    def troca(m: re.Match) -> str:
        destino, rotulo = m.group(1), m.group(2)
        alvo = INDICE.get(destino)
        if not alvo:
            # Nota ainda não escrita: vira um marcador visível, não um link quebrado.
            return f"`[[{destino}]]` :material-alert-circle:{{ title='nota ainda não escrita' }}"
        texto = rotulo or alvo["titulo"]
        return f"[{texto}]({_rel(src, alvo['src'])})"

    markdown = WIKILINK.sub(troca, markdown)

    # Backlinks só fazem sentido nas próprias notas.
    nota_id = _id_do_arquivo(Path(src))
    if nota_id and BACKLINKS.get(nota_id):
        linhas = ["", "---", "", "## Notas que apontam para esta", ""]
        for origem_id, titulo in sorted(BACKLINKS[nota_id], key=lambda t: t[1]):
            alvo = INDICE[origem_id]
            linhas.append(f"- [{titulo}]({_rel(src, alvo['src'])})")
        markdown += "\n".join(linhas) + "\n"

    return markdown
