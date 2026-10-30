"""Camada de dados do servidor: arquivos TXT, uma linha por registro, campos separados por '|'."""
from pathlib import Path

from .dominio import ItemEstoque, Livro, Loja

LOJAS = [
    ["paulista", "Livraria Paulista", "Av. Paulista, 1000 – São Paulo",
     "Seg a sáb, 10h às 22h; dom, 12h às 20h"],
    ["pinheiros", "Livraria Pinheiros", "Rua dos Pinheiros, 500 – São Paulo",
     "Todos os dias, 9h às 21h"],
]
LIVROS = [
    ["9788535902775", "Dom Casmurro", "Machado de Assis", "29.90"],
    ["9788571641149", "Memórias Póstumas de Brás Cubas", "Machado de Assis", "34.50"],
    ["9788535914641", "Grande Sertão: Veredas", "João Guimarães Rosa", "89.00"],
    ["9788501114775", "A Hora da Estrela", "Clarice Lispector", "39.90"],
]
ESTOQUE = [
    ["9788535902775", "paulista", "3"], ["9788535902775", "pinheiros", "0"],
    ["9788571641149", "paulista", "0"], ["9788535914641", "pinheiros", "2"],
    ["9788501114775", "paulista", "1"], ["9788501114775", "pinheiros", "5"],
]


class ArquivoTxt:
    def __init__(self, caminho, inicial=None):
        self.caminho = Path(caminho)
        if inicial is not None and not self.caminho.exists():
            self.gravar(inicial)

    def ler(self):
        if not self.caminho.exists():
            return []
        return [l.split("|") for l in self.caminho.read_text(encoding="utf-8").splitlines() if l.strip()]

    def gravar(self, registros):
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        texto = "\n".join("|".join(str(c).replace("|", "/") for c in r) for r in registros)
        self.caminho.write_text(texto + ("\n" if registros else ""), encoding="utf-8")


class Repositorio:
    def __init__(self, pasta):
        pasta = Path(pasta)
        self._livros = ArquivoTxt(pasta / "livros.txt", LIVROS)
        self._lojas = ArquivoTxt(pasta / "lojas.txt", LOJAS)
        self._estoque = ArquivoTxt(pasta / "estoque.txt", ESTOQUE)
        self._prefs = ArquivoTxt(pasta / "preferencias.txt")

    def livros(self):
        return [Livro(i, t, a, float(p)) for i, t, a, p in self._livros.ler()]

    def livro(self, isbn):
        return next((l for l in self.livros() if l.isbn == isbn), None)

    def lojas(self):
        return [Loja(*c) for c in self._lojas.ler()]

    def loja(self, loja_id):
        return next((l for l in self.lojas() if l.id == loja_id), None)

    def estoque_do_livro(self, isbn):
        return [ItemEstoque(i, l, int(q)) for i, l, q in self._estoque.ler() if i == isbn]

    def loja_favorita(self, cliente_id):
        return dict(self._prefs.ler()).get(cliente_id)

    def salvar_loja_favorita(self, cliente_id, loja_id):
        prefs = dict(self._prefs.ler())
        prefs[cliente_id] = loja_id
        self._prefs.gravar([[c, l] for c, l in prefs.items()])
