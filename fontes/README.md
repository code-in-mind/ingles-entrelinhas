# fontes/

Matéria-prima. **Nada aqui vai direto para o site ou para o livro.**

## `brutas/` — aulas de terceiros (fora do git)

Transcrições de aulas do YouTube que você usa para estudar. São obra de
outra pessoa: servem para você entender o tema e então escrever a sua
própria nota, com as suas palavras e os seus exemplos.

Isso não é formalidade. O livro vai ser vendido, e texto de terceiro
parafraseado de leve num produto pago é violação de direito autoral —
inclusive quando a fonte é um vídeo gratuito no YouTube. O que protege o
projeto é o material ser autoral de verdade, e o que garante isso é a
reescrita passar pela sua cabeça.

Por isso `fontes/brutas/` está no `.gitignore`.

## `podcasts/` — material próprio (versionado)

Transcrições dos episódios que você mesma gerou no NotebookLM e publicou no
YouTube. Esse conteúdo é seu: pode ir para o site e para o livro
integralmente, depois de revisado.

```bash
# aula de terceiro (estudo)
poetry run python scripts/fetch_transcript.py "https://youtu.be/XXX"

# seu próprio episódio (publicável)
poetry run python scripts/fetch_transcript.py "https://youtu.be/YYY" --podcast
```
