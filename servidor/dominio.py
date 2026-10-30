import unicodedata
from dataclasses import dataclass


def normalizar(texto):
    sem_acentos = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in sem_acentos if not unicodedata.combining(c)).casefold().strip()


class NaoEncontrado(Exception):
    pass


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str
    preco: float

    def corresponde(self, termo):
        termo = normalizar(termo)
        return termo in normalizar(self.titulo) or termo in normalizar(self.autor)


@dataclass(frozen=True)
class Loja:
    id: str
    nome: str
    endereco: str
    horario: str


@dataclass(frozen=True)
class ItemEstoque:
    isbn: str
    loja_id: str
    quantidade: int

    @property
    def disponivel(self):
        return self.quantidade > 0
