"""Regras de negócio do servidor, sem HTTP."""
import pytest

from servidor.casos_de_uso import Livraria
from servidor.dominio import NaoEncontrado
from servidor.repositorio import Repositorio

DOM, HORA = "9788535902775", "9788501114775"


@pytest.fixture
def livraria(tmp_path):
    return Livraria(Repositorio(tmp_path))


def test_busca_sem_acentos_e_por_autor(livraria):
    assert [l.titulo for l in livraria.buscar_livros("memorias")] == ["Memórias Póstumas de Brás Cubas"]
    assert len(livraria.buscar_livros("MACHADO")) == 2


def test_estoque_por_loja(livraria):
    itens = {i["loja"].id: i for i in livraria.disponibilidade(DOM)}
    assert itens["paulista"]["quantidade"] == 3 and not itens["pinheiros"]["disponivel"]


def test_favorita_primeiro_por_cliente(livraria):
    livraria.definir_loja_favorita("ana", "pinheiros")
    assert livraria.disponibilidade(HORA, "ana")[0]["loja"].id == "pinheiros"
    assert livraria.disponibilidade(HORA, "bia")[0]["loja"].id == "paulista"


def test_erros(livraria):
    with pytest.raises(NaoEncontrado, match="Livro não encontrado"):
        livraria.obter_livro("000")
    with pytest.raises(NaoEncontrado, match="Loja não encontrada"):
        livraria.definir_loja_favorita("ana", "centro")


def test_dados_em_txt(livraria, tmp_path):
    livraria.definir_loja_favorita("ana", "paulista")
    assert (tmp_path / "preferencias.txt").read_text(encoding="utf-8") == "ana|paulista\n"
    assert "Dom Casmurro" in (tmp_path / "livros.txt").read_text(encoding="utf-8")
