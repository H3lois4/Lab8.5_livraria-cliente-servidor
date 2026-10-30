# Livraria – Arquitetura Cliente-Servidor

MVP da livraria implementado na arquitetura **cliente-servidor** desenhada no exercício 8.1.

```
Cliente (navegador no computador ou no celular)
   │  requisições HTTP com JSON
   ▼
Servidor (Flask): rotas, casos de uso e regras de negócio
   │  lê e grava
   ▼
Dados: arquivos TXT (livros, lojas, estoque, preferências)
```

## Estrutura

| Pasta | Lado | O que faz |
|---|---|---|
| `cliente/` | Cliente | `index.html`, `app.js` e `style.css`. Monta as telas no navegador e chama a API com `fetch`. |
| `servidor/api.py` | Servidor | Rotas HTTP. Recebe a requisição e devolve **JSON** (nunca HTML). |
| `servidor/casos_de_uso.py` | Servidor | Regras de negócio do MVP. |
| `servidor/dominio.py` | Servidor | Entidades `Livro`, `Loja` e `ItemEstoque`. |
| `servidor/repositorio.py` | Servidor | Leitura e gravação dos arquivos TXT em `data/`. |

## API (contrato entre cliente e servidor)

| Método | Rota | Resposta |
|---|---|---|
| GET | `/api/livros?q=termo` | Lista de livros com preço |
| GET | `/api/livros/<isbn>` | Livro + estoque por loja (favorita primeiro) |
| GET | `/api/lojas` | Lojas com endereço e horário |
| GET | `/api/lojas/<id>` | Uma loja |
| GET | `/api/clientes/me/loja-favorita` | Loja favorita do cliente |
| PUT | `/api/clientes/me/loja-favorita` | Define a favorita (`{"loja_id": "..."}`) |

O cliente se identifica pelo cabeçalho `X-Cliente-Id` (um id gerado e guardado no navegador),
então o servidor não precisa manter sessão. Erros voltam como `{"erro": "..."}` com 400 ou 404.

Para facilitar o deploy, o servidor também entrega os arquivos da pasta `cliente/` no mesmo
endereço. Como a API libera CORS, o cliente também pode ser hospedado em outro lugar: basta
definir `window.API_URL` no `index.html`.

## Como rodar

```bash
pip install -r requirements.txt
pytest -v        # regras, contrato da API e separação cliente-servidor
python app.py    # http://localhost:5000
```
