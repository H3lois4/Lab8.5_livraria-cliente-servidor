"""Ponto de entrada para produção (ex.: Azure App Service com Gunicorn)."""
from servidor import create_app

app = create_app()
