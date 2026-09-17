.PHONY: install cards serve build anki book clean all help

help:          ## Lista os comandos disponíveis
	@grep -E '^[a-z-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "};{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install:       ## Instala as dependências
	poetry install --no-root

cards:         ## Gera as páginas de flashcards a partir de cartoes/*.yml
	poetry run python scripts/build_flashcards.py

serve: cards   ## Sobe o site local com recarga automática
	poetry run mkdocs serve

build: cards   ## Constrói o site em site/
	poetry run mkdocs build --strict

anki:          ## Exporta o baralho .apkg
	poetry run python scripts/export_anki.py

book: cards    ## Monta o manuscrito e gera EPUB + PDF + DOCX
	poetry run python scripts/build_book.py --all

clean:         ## Remove os artefatos gerados
	rm -rf site livro/saida

all: build anki book
