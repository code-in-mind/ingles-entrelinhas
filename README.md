# Inglês Entrelinhas

Curso de inglês geral do **A1 ao C1**, construído pelo método **Zettelkasten**,
que gera dois produtos a partir de uma única fonte de Markdown:

- um **site** em MkDocs Material (textos, flashcards, exercícios, podcasts)
- um **livro** em EPUB/PDF, organizado por módulos, pronto para venda

## A regra de ouro do projeto

**Nada é escrito duas vezes.** O site e o livro saem dos mesmos arquivos; os
flashcards do site, do Anki e do livro saem do mesmo YAML. Se você se pegar
copiando conteúdo de um lugar para outro, é sinal de que falta um script.

## Estrutura

```
docs/notas/        zettels atômicos — o coração do projeto
docs/modulos/      caminhos de leitura (viram capítulos do livro)
docs/podcasts/     episódios + transcrição revisada
cartoes/           flashcards em YAML (fonte única)
fontes/            matéria-prima: transcrições do YouTube
scripts/           os geradores
livro/             metadados, CSS, filtro Lua e saída do livro
```

## Começando

```bash
poetry install --no-root
make serve          # http://127.0.0.1:8000
```

## Comandos do dia a dia

| Comando | O que faz |
| --- | --- |
| `make serve` | sobe o site local com recarga automática |
| `make cards` | regenera as páginas de flashcards a partir do YAML |
| `make anki` | exporta o baralho `.apkg` |
| `make book` | monta o manuscrito e gera EPUB + PDF + DOCX (localmente, para conferir) |
| `make build` | build de produção (`--strict`) |
| `make help` | lista todos os alvos disponíveis |
| `poetry run python scripts/new_note.py "Título" --level A2` | cria um zettel novo com ID |
| `poetry run python scripts/fetch_transcript.py URL` | baixa e limpa uma transcrição |

## O fluxo de trabalho

1. **Alimentar o NotebookLM** com os documentos e vídeos do tema.
2. **Gerar o episódio** de podcast e publicá-lo no YouTube.
3. **Baixar a transcrição** — a das aulas de terceiros para estudar
   (`fontes/brutas/`, fora do git), a dos seus episódios para publicar
   (`fontes/podcasts/`).
4. **Escrever as notas** com `scripts/new_note.py`, uma ideia por nota,
   ligando com `[[ID]]`.
5. **Costurar o módulo**: o `index.md` do módulo conta a história usando
   as notas; os exercícios e os flashcards vêm junto.
6. **Publicar o site**: `git push` — o GitHub Actions constrói e publica no Pages.
7. **Publicar o livro**: crie uma tag (`git tag v1.0.0 && git push origin v1.0.0`) — o GitHub gera os 3 formatos e publica a Release sozinho.

## Como os wikilinks funcionam

Escreva `[[202609161430]]` em qualquer página. O hook
`scripts/zettel_hooks.py` resolve o link no site e, de quebra, monta a seção
**"Notas que apontam para esta"** no fim de cada zettel. No livro, o mesmo
wikilink vira referência cruzada para o apêndice.

O ID (`AAAAMMDDHHMM`) nunca muda, mesmo que o título mude. É a única decisão
irreversível do projeto.

## Direito autoral

Transcrições de aulas de terceiros são **fonte de estudo**, não conteúdo.
Elas ficam em `fontes/brutas/`, fora do git e fora do site, e servem para
você entender o tema e escrever a nota com as suas palavras. Só material
autoral — e os seus próprios podcasts — vai para o livro que será vendido.
Veja `fontes/README.md`.

## Publicação do site

O workflow `.github/workflows/deploy.yml` publica o **site** a cada push na
`main`: constrói com `mkdocs build --strict` e sobe no GitHub Pages. No
repositório, vá em **Settings → Pages → Source: GitHub Actions** uma vez —
depois disso é automático para sempre.

## Geração do livro (EPUB + PDF + DOCX)

Isto é **separado** do site, porque o livro tem uma saída diferente (três
arquivos para baixar, não uma página). O workflow
`.github/workflows/book.yml` cuida disso:

| Quando roda | O que faz |
| --- | --- |
| Todo push na `main` | Gera os 3 formatos e anexa como *artefato* do workflow — baixável na aba **Actions → (o run) → Artifacts**, por 90 dias. Serve para conferir o resultado a cada mudança. |
| Você cria uma tag `v1.0.0`, `v1.1.0`... | Além de gerar, publica uma **GitHub Release** com os 3 arquivos anexados — link fixo e público para baixar aquela edição. |
| Botão "Run workflow" na aba Actions | Roda na hora, sem precisar de push nem tag. |

Ou seja: **você não precisa rodar `make book` na sua máquina** para o livro
sair atualizado — isso só é útil para conferir localmente antes de subir. O
GitHub gera de novo sozinho a cada push.

### Como lançar uma edição oficial

```bash
git tag v1.0.0
git push origin v1.0.0
```

Isso dispara o workflow, que cria a Release "v1.0.0" com `livro.epub`,
`livro.pdf` e `livro.docx` anexados — é esse link que você usa para vender
ou distribuir aquela versão. Da próxima vez que o conteúdo mudar bastante,
repita com `v1.1.0`, `v2.0.0`, etc. — não existe uma regra fixa de quando
subir a versão, é critério de vocês dois.

### Para que serve cada formato

- **`.epub`** — o formato principal de venda. Aceito por Kindle (a Amazon
  aceita EPUB como fonte desde 2022), Google Play Books, Apple Books, Kobo.
- **`.pdf`** — para impressão sob demanda ou venda direta em PDF, com
  layout fixo (bom para quem vai ler no computador ou imprimir).
- **`.docx`** — não é para vender: é para mandar para quem revisa ou
  diagrama o livro e não mexe com Markdown/Git. Se quiserem um visual mais
  trabalhado no Word, coloquem um arquivo `livro/referencia.docx` com os
  estilos de título e corpo que preferirem — o Pandoc herda o estilo dele
  automaticamente.

## Equipe

- [@LorenadeCastro](https://github.com/LorenadeCastro) — Lorena de Castro
- [@gabrielbdornas](https://github.com/gabrielbdornas) — Gabriel Dornas
