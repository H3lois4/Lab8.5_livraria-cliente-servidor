// Lado CLIENTE: monta as telas no navegador e fala com o servidor só por HTTP/JSON.
const API = window.API_URL || "";
const tela = document.getElementById("tela");
const aviso = document.getElementById("aviso");

// ---------- Identificação do cliente (guardada no navegador) ----------
function clienteId() {
  let id = null;
  try { id = localStorage.getItem("cliente_id"); } catch (e) {}
  if (!id) {
    id = (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random()).replace(/-/g, "");
    try { localStorage.setItem("cliente_id", id); } catch (e) {}
  }
  return id;
}
const CLIENTE = clienteId();

// ---------- Comunicação com o servidor ----------
async function api(caminho, opcoes = {}) {
  const resposta = await fetch(API + caminho, {
    ...opcoes,
    headers: { "Content-Type": "application/json", "X-Cliente-Id": CLIENTE, ...(opcoes.headers || {}) },
  });
  const dados = await resposta.json();
  if (!resposta.ok) throw new Error(dados.erro || "Erro ao falar com o servidor");
  return dados;
}

// ---------- Utilidades de exibição ----------
const moeda = (v) => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function mostrarAviso(texto, erro = false) {
  aviso.textContent = texto;
  aviso.className = "aviso" + (erro ? " erro" : "");
  aviso.hidden = false;
}

function botaoFavorita(lojaId, favorita, grande = false) {
  return favorita
    ? `<p class="fav">Sua loja favorita</p>`
    : `<button class="${grande ? "" : "secundario"}" data-favoritar="${esc(lojaId)}">Definir como favorita</button>`;
}

// ---------- Telas ----------
async function telaBusca(termo = "") {
  const livros = await api(`/api/livros?q=${encodeURIComponent(termo)}`);
  tela.innerHTML = `
    <h1>Veja se o livro está na loja antes de sair de casa</h1>
    <form class="busca" id="form-busca">
      <input type="search" name="q" value="${esc(termo)}" placeholder="Título ou autor" aria-label="Título ou autor">
      <button>Buscar</button>
    </form>
    ${livros.length ? `<ul class="lista">${livros.map((l) => `
      <li class="cartao">
        <div class="linha">
          <a class="titulo" href="#/livros/${esc(l.isbn)}">${esc(l.titulo)}</a>
          <span class="preco">${moeda(l.preco)}</span>
        </div>
        <p class="suave">${esc(l.autor)}</p>
      </li>`).join("")}</ul>`
    : `<p class="suave">Nenhum livro encontrado. Tente outro título ou o nome do autor.</p>`}`;
  document.getElementById("form-busca").addEventListener("submit", (e) => {
    e.preventDefault();
    const q = new FormData(e.target).get("q");
    location.hash = q ? `#/?q=${encodeURIComponent(q)}` : "#/";
  });
}

async function telaLivro(isbn) {
  const { livro, disponibilidade } = await api(`/api/livros/${encodeURIComponent(isbn)}`);
  tela.innerHTML = `
    <p><a href="#/">Voltar para a busca</a></p>
    <h1>${esc(livro.titulo)}</h1>
    <p class="suave">${esc(livro.autor)}</p>
    <p class="preco grande">${moeda(livro.preco)} <span class="suave">em todas as lojas</span></p>
    <h2>Disponibilidade</h2>
    <ul class="lista">${disponibilidade.map((i) => `
      <li class="cartao">
        <div class="linha">
          <a href="#/lojas/${esc(i.loja.id)}">${esc(i.loja.nome)}</a>
          ${i.disponivel ? `<span class="sim">${i.quantidade} em estoque</span>` : `<span class="nao">Esgotado</span>`}
        </div>
        <p class="suave">${esc(i.loja.endereco)}</p>
        ${botaoFavorita(i.loja.id, i.favorita)}
      </li>`).join("")}
    </ul>`;
}

async function telaLojas() {
  const [lojas, { loja_id: favorita }] = await Promise.all([
    api("/api/lojas"), api("/api/clientes/me/loja-favorita"),
  ]);
  tela.innerHTML = `
    <h1>Lojas</h1>
    <ul class="lista">${lojas.map((l) => `
      <li class="cartao">
        <a class="titulo" href="#/lojas/${esc(l.id)}">${esc(l.nome)}</a>
        <p>${esc(l.endereco)}</p>
        <p class="suave">${esc(l.horario)}</p>
        ${botaoFavorita(l.id, l.id === favorita)}
      </li>`).join("")}
    </ul>`;
}

async function telaLoja(id) {
  const [loja, { loja_id: favorita }] = await Promise.all([
    api(`/api/lojas/${encodeURIComponent(id)}`), api("/api/clientes/me/loja-favorita"),
  ]);
  tela.innerHTML = `
    <p><a href="#/lojas">Todas as lojas</a></p>
    <h1>${esc(loja.nome)}</h1>
    <h2>Endereço</h2><p>${esc(loja.endereco)}</p>
    <h2>Horário de funcionamento</h2><p>${esc(loja.horario)}</p>
    ${botaoFavorita(loja.id, loja.id === favorita, true)}`;
}

// ---------- Ações ----------
tela.addEventListener("click", async (e) => {
  const botao = e.target.closest("[data-favoritar]");
  if (!botao) return;
  try {
    const r = await api("/api/clientes/me/loja-favorita", {
      method: "PUT", body: JSON.stringify({ loja_id: botao.dataset.favoritar }),
    });
    await rotear();
    mostrarAviso(r.mensagem);
  } catch (erro) {
    mostrarAviso(erro.message, true);
  }
});

// ---------- Navegação ----------
async function rotear() {
  aviso.hidden = true;
  const [caminho, consulta = ""] = location.hash.replace(/^#/, "").split("?");
  const partes = caminho.split("/").filter(Boolean);
  try {
    if (partes[0] === "livros" && partes[1]) await telaLivro(decodeURIComponent(partes[1]));
    else if (partes[0] === "lojas" && partes[1]) await telaLoja(decodeURIComponent(partes[1]));
    else if (partes[0] === "lojas") await telaLojas();
    else await telaBusca(new URLSearchParams(consulta).get("q") || "");
  } catch (erro) {
    tela.innerHTML = `<h1>${esc(erro.message)}</h1><p><a href="#/">Voltar para a busca</a></p>`;
  }
}

window.addEventListener("hashchange", rotear);
rotear();
