---
title: O método
---

# Por que Zettelkasten para aprender inglês

Zettelkasten ("caixa de fichas") é o método de Niklas Luhmann: em vez de
resumir capítulos, você escreve **fichas atômicas** — uma ideia por ficha,
com as suas palavras — e as **liga umas às outras**. O conhecimento não
fica organizado por assunto; fica organizado por conexão.

Para idioma isso funciona especialmente bem, por três motivos.

**Gramática não é hierárquica.** Um sumário de livro finge que *Present
Perfect* vem depois de *Past Simple* e antes de *Passive Voice*. Na
prática, entender *Present Perfect* exige entender `for` e `since`, que
exigem entender duração, que reaparece em *Present Perfect Continuous*
três módulos adiante. A rede descreve isso; a lista, não.

**Você vai reencontrar a mesma dúvida várias vezes.** Com nota atômica,
você não reescreve — você linka. A terceira vez que `for` vs `since`
aparecer, ela já está pronta, e o backlink te mostra que aquilo apareceu em
três contextos diferentes. Isso é sinal de que o tema é importante.

**O livro se escreve sozinho.** Notas conectadas já são um rascunho: a
sequência de links vira a sequência de parágrafos. É exatamente o que
Luhmann dizia dos próprios artigos.

## As três regras

!!! note "1. Atomicidade"
    Uma nota = uma ideia. Se você precisa de "e também" para continuar,
    são duas notas.

!!! note "2. Autonomia"
    A nota tem que fazer sentido para quem abre ela primeiro, sem contexto.
    Por isso ela nunca começa com "como vimos acima".

!!! note "3. Conexão explícita"
    Link sem explicação é link morto. Escreva *por que* as duas notas se
    ligam: "— as preposições que quase sempre acompanham este tempo verbal".

## O ID nunca muda

O nome do arquivo começa com um carimbo de tempo, `202609161430`. O título
pode mudar, o texto pode ser reescrito, a nota pode mudar de módulo — o ID
continua o mesmo, e todos os `[[links]]` continuam válidos. É a única
decisão do projeto que é praticamente irreversível, então ela é a única que
foi tomada logo no começo.

Para criar uma nota já no padrão:

```bash
poetry run python scripts/new_note.py "For vs Since" --tags gramatica preposicoes --level B1
```
