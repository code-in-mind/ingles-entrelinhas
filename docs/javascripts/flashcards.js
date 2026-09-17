// Vira o cartão no clique ou no Enter/Espaço.
// Usa delegação de evento para funcionar com navigation.instant do Material,
// que troca o conteúdo da página sem recarregar o documento.

document.addEventListener("click", (e) => {
  const cartao = e.target.closest(".flashcard");
  if (cartao) cartao.classList.toggle("virado");
});

document.addEventListener("keydown", (e) => {
  if (e.key !== "Enter" && e.key !== " ") return;
  const cartao = document.activeElement?.closest?.(".flashcard");
  if (cartao) {
    e.preventDefault();
    cartao.classList.toggle("virado");
  }
});
