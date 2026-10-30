"""Lado SERVIDOR: API HTTP/JSON com as regras de negócio e os dados (arquivos TXT).
Não gera HTML: quem monta a tela é o cliente."""
from .api import create_app

__all__ = ["create_app"]
