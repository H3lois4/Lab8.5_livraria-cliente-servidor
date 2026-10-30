"""Contrato HTTP/JSON entre cliente e servidor."""
import pytest

from servidor import create_app

DOM, HORA = "9788535902775", "9788501114775"


@pytest.fixture
def http(tmp_path):
    return create_app(tmp_path).test_client()


def test_buscar_livros(http):
    r = http.get("/api/livros?q=clarice")
    assert r.status_code == 200 and r.is_json
    assert r.json == [{"isbn": HORA, "titulo": "A Hora da Estrela",
                       "autor": "Clarice Lispector", "preco": 39.9}]


def test_detalhe_com_estoque_e_preco(http):
    dados = http.get(f"/api/livros/{DOM}").json
    assert dados["livro"]["preco"] == 29.9
    por_loja = {i["loja"]["id"]: i for i in dados["disponibilidade"]}
    assert por_loja["paulista"]["quantidade"] == 3 and not por_loja["pinheiros"]["disponivel"]


def test_lojas(http):
    assert [l["id"] for l in http.get("/api/lojas").json] == ["paulista", "pinheiros"]
    assert http.get("/api/lojas/pinheiros").json["horario"] == "Todos os dias, 9h às 21h"


def test_erros_404_em_json(http):
    for url in ("/api/livros/000", "/api/lojas/centro"):
        r = http.get(url)
        assert r.status_code == 404 and "erro" in r.json


def test_loja_favorita_pelo_cabecalho(http):
    cab = {"X-Cliente-Id": "ana"}
    r = http.put("/api/clientes/me/loja-favorita", json={"loja_id": "pinheiros"}, headers=cab)
    assert r.json["mensagem"] == "Livraria Pinheiros agora é sua loja favorita."
    assert http.get("/api/clientes/me/loja-favorita", headers=cab).json == {"loja_id": "pinheiros"}
    primeira = http.get(f"/api/livros/{HORA}", headers=cab).json["disponibilidade"][0]
    assert primeira["loja"]["id"] == "pinheiros" and primeira["favorita"]
    outro = http.get(f"/api/livros/{HORA}", headers={"X-Cliente-Id": "bia"}).json
    assert outro["disponibilidade"][0]["loja"]["id"] == "paulista"


def test_favorita_exige_identificacao(http):
    r = http.put("/api/clientes/me/loja-favorita", json={"loja_id": "paulista"})
    assert r.status_code == 400


def test_favorita_inexistente(http):
    r = http.put("/api/clientes/me/loja-favorita", json={"loja_id": "centro"},
                 headers={"X-Cliente-Id": "ana"})
    assert r.status_code == 404 and r.json["erro"] == "Loja não encontrada"


def test_cors_permite_cliente_em_outro_endereco(http):
    assert http.get("/api/lojas").headers["Access-Control-Allow-Origin"] == "*"
    r = http.options("/api/clientes/me/loja-favorita")
    assert r.status_code in (200, 204)
    assert "X-Cliente-Id" in r.headers["Access-Control-Allow-Headers"]


def test_servidor_entrega_o_cliente(http):
    assert b"app.js" in http.get("/").data
    assert http.get("/app.js").status_code == 200
