"""
Baixa a legenda de um vídeo do YouTube e devolve texto limpo em fontes/.

    poetry run python scripts/fetch_transcript.py "https://youtu.be/ABC123"
    poetry run python scripts/fetch_transcript.py "https://youtu.be/ABC123" --lang pt

Dois usos no projeto:

1. AULAS DE TERCEIROS  -> vira MATÉRIA-PRIMA DE ESTUDO, em fontes/brutas/
   (fora do git, fora do site, fora do livro). Você lê, entende e escreve
   a nota com as SUAS palavras. Transcrição de aula alheia é obra de
   terceiro: não pode ir para um livro pago, nem parafraseada de leve.

2. SEUS PRÓPRIOS PODCASTS -> vira CONTEÚDO PUBLICÁVEL, em fontes/podcasts/.
   Aí sim entra no site e no livro, porque o material é seu.

O texto vem sem pontuação e picotado em linhas de legenda. O script
remonta os parágrafos; a revisão final é humana.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTES = RAIZ / "fontes"

# 00:00:12,340 --> 00:00:15,110
TEMPO = re.compile(r"^\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->")
TAGS = re.compile(r"<[^>]+>")


def baixar_legenda(url: str, lang: str, pasta: Path) -> Path:
    """Chama o yt-dlp pedindo só a legenda, sem baixar o vídeo."""
    comando = [
        "yt-dlp",
        "--skip-download",          # não queremos o vídeo, só o texto
        "--write-sub",              # legenda oficial, se existir
        "--write-auto-sub",         # senão, a automática
        "--sub-lang", lang,
        "--convert-subs", "srt",    # formato fácil de limpar
        "-o", str(pasta / "%(id)s.%(ext)s"),
        url,
    ]
    subprocess.run(comando, check=True)
    encontrados = list(pasta.glob("*.srt"))
    if not encontrados:
        sys.exit("Nenhuma legenda disponível para esse vídeo/idioma.")
    return encontrados[0]


def limpar(srt: str) -> str:
    """Tira numeração, marcas de tempo, tags e repetições do rolling caption."""
    linhas: list[str] = []
    for bruta in srt.splitlines():
        linha = TAGS.sub("", bruta).strip()
        if not linha or linha.isdigit() or TEMPO.match(linha):
            continue
        # A legenda automática repete a linha anterior enquanto rola na tela.
        if linhas and linha == linhas[-1]:
            continue
        linhas.append(linha)

    texto = " ".join(linhas)
    texto = re.sub(r"\s+", " ", texto).strip()
    # Quebra de parágrafo depois de ponto final, para ficar legível.
    texto = re.sub(r"(?<=[.!?]) (?=[A-Z])", "\n\n", texto)
    return texto


def main() -> None:
    p = argparse.ArgumentParser(description="Transcrição de vídeo do YouTube.")
    p.add_argument("url")
    p.add_argument("--lang", default="en")
    p.add_argument("--podcast", action="store_true",
                   help="material próprio: salva em fontes/podcasts/ (publicável)")
    args = p.parse_args()

    destino_dir = FONTES / ("podcasts" if args.podcast else "brutas")
    destino_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        srt = baixar_legenda(args.url, args.lang, Path(tmp))
        texto = limpar(srt.read_text(encoding="utf-8"))
        destino = destino_dir / f"{srt.stem.split('.')[0]}.md"

    cabecalho = (
        f"<!-- origem: {args.url} -->\n"
        f"<!-- {'material próprio — publicável' if args.podcast else 'MATÉRIA-PRIMA: não publicar, reescrever'} -->\n\n"
    )
    destino.write_text(cabecalho + texto + "\n", encoding="utf-8")

    palavras = len(texto.split())
    print(f"{palavras} palavras -> {destino.relative_to(RAIZ)}")
    if not args.podcast:
        print("Lembrete: este texto é fonte de estudo. Reescreva antes de publicar.")


if __name__ == "__main__":
    main()
