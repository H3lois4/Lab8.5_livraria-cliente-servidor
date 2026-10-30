"""Rotas HTTP do servidor. Toda resposta é JSON; o cliente decide como exibir."""
import os
from dataclasses import asdict
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from .casos_de_uso import Livraria
from .dominio import NaoEncontrado
from .repositorio import Repositorio

PASTA_CLIENTE = Path(__file__).resolve().parent.parent / "cliente"


def _item_json(item):
    return {"loja": asdict(item["loja"]), "quantidade": item["quantidade"],
            "disponivel": item["disponivel"], "favorita": item["favorita"]}


def create_app(pasta_dados=None, servir_cliente=True):
    pasta_dados = pasta_dados or os.environ.get("PASTA_DADOS", "data")
    livraria = Livraria(Repositorio(pasta_dados))
    app = Flask(__name__, static_folder=None)

    def cliente_id():
        """O cliente se identifica pelo cabeçalho X-Cliente-Id (o servidor não guarda sessão)."""
        return request.headers.get("X-Cliente-Id") or None

    def exigir_cliente():
        cid = cliente_id()
        if not cid:
            return None, (jsonify(erro="Cabeçalho X-Cliente-Id é obrigatório"), 400)
        return cid, None

    @app.errorhandler(NaoEncontrado)
    def nao_encontrado(erro):
        return jsonify(erro=str(erro)), 404

    @app.after_request
    def cors(resposta):
        # permite que o cliente seja hospedado em outro endereço
        resposta.headers["Access-Control-Allow-Origin"] = "*"
        resposta.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Cliente-Id"
        resposta.headers["Access-Control-Allow-Methods"] = "GET, PUT, OPTIONS"
        return resposta

    # ---------- Livros ----------
    @app.get("/api/livros")
    def buscar_livros():
        return jsonify([asdict(l) for l in livraria.buscar_livros(request.args.get("q", ""))])

    @app.get("/api/livros/<isbn>")
    def detalhe_livro(isbn):
        livro = livraria.obter_livro(isbn)
        itens = livraria.disponibilidade(isbn, cliente_id())
        return jsonify(livro=asdict(livro), disponibilidade=[_item_json(i) for i in itens])

    # ---------- Lojas ----------
    @app.get("/api/lojas")
    def listar_lojas():
        return jsonify([asdict(l) for l in livraria.listar_lojas()])

    @app.get("/api/lojas/<loja_id>")
    def detalhe_loja(loja_id):
        return jsonify(asdict(livraria.obter_loja(loja_id)))

    # ---------- Cliente ----------
    @app.get("/api/clientes/me/loja-favorita")
    def obter_favorita():
        return jsonify(loja_id=livraria.loja_favorita(cliente_id()))

    @app.put("/api/clientes/me/loja-favorita")
    def definir_favorita():
        cid, erro = exigir_cliente()
        if erro:
            return erro
        dados = request.get_json(silent=True) or {}
        loja = livraria.definir_loja_favorita(cid, dados.get("loja_id", ""))
        return jsonify(loja_id=loja.id, mensagem=f"{loja.nome} agora é sua loja favorita.")

    @app.route("/api/<path:_>", methods=["OPTIONS"])
    def preflight(_):
        return "", 204

    # ---------- Arquivos do cliente (opcional: mesmo endereço para facilitar o deploy) ----------
    if servir_cliente:
        @app.get("/")
        def pagina_inicial():
            return send_from_directory(PASTA_CLIENTE, "index.html")

        @app.get("/<path:arquivo>")
        def arquivos_cliente(arquivo):
            return send_from_directory(PASTA_CLIENTE, arquivo)

    return app
