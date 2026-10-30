"""Sobe o servidor (API) e, no mesmo endereço, entrega os arquivos do cliente."""
from servidor import create_app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
