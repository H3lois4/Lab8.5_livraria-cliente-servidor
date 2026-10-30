"""Garante a separação cliente-servidor."""
import ast
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def test_servidor_nao_gera_html():
    for arquivo in (RAIZ / "servidor").glob("*.py"):
        assert "render_template" not in arquivo.read_text(encoding="utf-8")


def test_regras_ficam_fora_das_rotas():
    arvore = ast.parse((RAIZ / "servidor" / "api.py").read_text(encoding="utf-8"))
    importados = {n.module for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom)}
    assert ".repositorio" not in importados or "casos_de_uso" in importados


def test_cliente_so_conversa_com_a_api():
    js = (RAIZ / "cliente" / "app.js").read_text(encoding="utf-8")
    chamadas = re.findall(r'api\(\s*[`"]([^`"]+)', js)
    assert chamadas and all(c.startswith("/api/") for c in chamadas)
