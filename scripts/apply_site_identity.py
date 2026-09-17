"""
Propaga config/site.yml para os arquivos que precisam do nome do projeto,
da organização e dos autores em texto estático (mkdocs.yml, o livro, o
pyproject, o README, o CODEOWNERS, o site).

    poetry run python scripts/apply_site_identity.py

Por que existe: mkdocs.yml e livro/metadata.yaml são lidos por ferramentas
de terceiros (MkDocs, Pandoc) que não sabem importar config/site.yml
sozinhas. Este script é a ponte — ele casa cada arquivo pelo FORMATO da
linha (ex.: `site_name: ...`), não pelo valor antigo, então funciona em
qualquer renomeação ou troca de organização futura, não só nesta.

Os scripts que geram conteúdo em tempo de execução (build_book.py,
export_anki.py) não precisam disso: eles importam config/site.yml
diretamente e nunca ficam desatualizados.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = yaml.safe_load((RAIZ / "config" / "site.yml").read_text(encoding="utf-8"))


def trocar(caminho: Path, *pares: tuple[str, str]) -> None:
    """Aplica uma lista de (padrão_regex, substituição) e reporta o que mudou."""
    texto = caminho.read_text(encoding="utf-8")
    original = texto
    for padrao, novo in pares:
        texto = re.sub(padrao, novo, texto, flags=re.M)
    if texto != original:
        caminho.write_text(texto, encoding="utf-8")
        print(f"atualizado: {caminho.relative_to(RAIZ)}")
    else:
        print(f"sem mudança: {caminho.relative_to(RAIZ)}")


def main() -> None:
    c = CONFIG
    org = c["github_org"]
    url_site = f"https://{org.lower()}.github.io/{c['repo_slug']}/"
    url_repo = f"https://github.com/{org}/{c['repo_slug']}"
    mantenedores = c["maintainers"]
    autor_principal = mantenedores[0]["nome"]
    nomes_autores = " e ".join(m["nome"] for m in mantenedores)

    # ------------------------------------------------------------ mkdocs.yml
    trocar(
        RAIZ / "mkdocs.yml",
        (r"^site_name:.*$", f"site_name: {c['name']}"),
        (r"^site_url:.*$", f"site_url: {url_site}"),
        (r"^repo_url:.*$", f"repo_url: {url_repo}"),
        (r"^repo_name:.*$", f"repo_name: {org}/{c['repo_slug']}"),
        (r"^site_author:.*$", f"site_author: {autor_principal}"),
    )
    # Ícones sociais: um link para a organização + um para cada mantenedor.
    caminho = RAIZ / "mkdocs.yml"
    texto = caminho.read_text(encoding="utf-8")
    bloco_social = "\n".join(
        [
            "  social:",
            f"    - icon: fontawesome/brands/github",
            f"      link: https://github.com/{org}",
            *[
                f"    - icon: fontawesome/brands/github\n"
                f"      link: https://github.com/{m['handle']}\n"
                f"      name: {m['nome']}"
                for m in mantenedores
            ],
            "    - icon: fontawesome/brands/youtube",
            "      link: https://youtube.com/@ingles-em-notas",
        ]
    )
    texto = re.sub(r"  social:\n(?:    -.*\n(?:      .*\n)*)+", bloco_social + "\n", texto)
    if texto != caminho.read_text(encoding="utf-8"):
        caminho.write_text(texto, encoding="utf-8")
        print("atualizado: mkdocs.yml (ícones sociais)")

    # ------------------------------------------------------- livro/metadata.yaml
    trocar(
        RAIZ / "livro" / "metadata.yaml",
        (r'^title:.*$', f'title: "{c["name"]}"'),
        (r'^subtitle:.*$', f'subtitle: "{c["tagline"]}"'),
        (r'^author:.*$', f'author: "{nomes_autores}"'),
        (r'^rights:.*$', f'rights: "© 2026 {nomes_autores}. Todos os direitos reservados."'),
    )

    # ------------------------------------------------------------ pyproject.toml
    lista_autores = ", ".join(f'"{m["nome"]} <{m["handle"]}@users.noreply.github.com>"' for m in mantenedores)
    trocar(
        RAIZ / "pyproject.toml",
        (r'^name = .*$', f'name = "{c["repo_slug"]}"'),
        (r'^authors = \[.*\]$', f'authors = [{lista_autores}]'),
    )

    # ------------------------------------------------------------------ README.md
    trocar(RAIZ / "README.md", (r"^# .*$", f"# {c['name']}"))

    # Seção "## Equipe" — cria se não existir, substitui se existir.
    caminho = RAIZ / "README.md"
    texto = caminho.read_text(encoding="utf-8")
    linhas_equipe = "\n".join(
        f"- [@{m['handle']}](https://github.com/{m['handle']}) — {m['nome']}"
        for m in mantenedores
    )
    bloco_equipe = f"## Equipe\n\n{linhas_equipe}\n"
    if "## Equipe" in texto:
        texto = re.sub(r"## Equipe\n\n(?:- .*\n)+", bloco_equipe, texto)
    else:
        texto = texto.rstrip("\n") + "\n\n" + bloco_equipe
    if texto != caminho.read_text(encoding="utf-8"):
        caminho.write_text(texto, encoding="utf-8")
        print("atualizado: README.md (seção Equipe)")

    # -------------------------------------------------------------- docs/index.md
    trocar(
        RAIZ / "docs" / "index.md",
        (r"^title:.*$", f"title: {c['name']}"),
        (r"^# .*$", f"# {c['name']}"),
    )

    # --------------------------------------------------------- docs/podcasts/index.md
    trocar(
        RAIZ / "docs" / "podcasts" / "index.md",
        (r"^# Podcast — .*$", f"# Podcast — {c['name']}"),
    )

    # --------------------------------------------------------------- .github/CODEOWNERS
    caminho = RAIZ / ".github" / "CODEOWNERS"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    handles = " ".join(f"@{m['handle']}" for m in mantenedores)
    conteudo_novo = (
        "# Gerado por scripts/apply_site_identity.py a partir de config/site.yml.\n"
        "# Qualquer alteração no repositório precisa de revisão de um dos dois.\n"
        f"* {handles}\n"
    )
    conteudo_atual = caminho.read_text(encoding="utf-8") if caminho.exists() else None
    if conteudo_atual != conteudo_novo:
        caminho.write_text(conteudo_novo, encoding="utf-8")
        print("atualizado: .github/CODEOWNERS")
    else:
        print("sem mudança: .github/CODEOWNERS")

    print(f"\nOrganização: {org}   Repositório: {url_repo}")
    print("Concluído. Revise o diff antes de commitar.")


if __name__ == "__main__":
    main()
