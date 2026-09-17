-- Filtro Pandoc: limpa da versão impressa o que só existe na tela.
--
-- 1. Remove os ícones do Material (:material-xxx:), que no livro
--    apareceriam como texto solto sem sentido.
-- 2. Remove blocos de HTML cru que tenham sobrado da conversão.
-- 3. Transforma o atributo {#nota-ID} em âncora de referência cruzada.

function Str(elem)
  -- :material-headphones: e similares somem
  local limpo = elem.text:gsub(":material%-[%w%-]+:", "")
  limpo = limpo:gsub(":fontawesome%-[%w%-%.]+:", "")
  if limpo ~= elem.text then
    return pandoc.Str(limpo)
  end
end

function RawBlock(elem)
  if elem.format == "html" then
    return {}  -- descarta HTML cru no livro
  end
end

function RawInline(elem)
  if elem.format == "html" then
    return {}
  end
end

function Header(elem)
  -- Marca os capítulos de nível 1 para quebrar página (via CSS/LaTeX)
  if elem.level == 1 then
    elem.classes:insert("capitulo")
  end
  return elem
end

-- ~~texto riscado~~ funciona nativamente em EPUB e DOCX (HTML/OOXML), mas em
-- PDF o Pandoc precisa do pacote LaTeX "soul", que nem sempre está disponível.
-- Em vez de depender de mais uma instalação de sistema, a saída PDF usa
-- itálico no lugar do rasurado — mantém o efeito de "isto está errado" sem
-- a dependência extra.
function Strikeout(elem)
  if FORMAT:match("latex") then
    return pandoc.Emph(elem.content)
  end
  return elem
end
