---
title: Caderno de notas
---

# Caderno de notas

Cada nota trata de **uma ideia só** e pode ser lida fora de ordem. No fim de
cada uma há os *backlinks* — as notas que apontam para ela. Siga-os: é ali
que a rede te mostra o que você ainda não sabia que precisava saber.

| Nota | Nível | Sobre |
| --- | --- | --- |
| [[202609161535]] | A1 | A base de tudo: `am`, `is`, `are` |
| [[202609161610]] | A1 | `a`, `an`, `the` — som, não letra |
| [[202609161430]] | B1 | O passado que acabou vs. o passado que continua |
| [[202609161502]] | B1 | Duração vs. ponto de partida |

!!! tip "Criando uma nota"
    ```bash
    poetry run python scripts/new_note.py "Título da nota" --tags gramatica --level A2
    ```
    O script gera o ID, o front matter e o esqueleto. Você só escreve.
