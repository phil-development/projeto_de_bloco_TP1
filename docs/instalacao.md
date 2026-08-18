# Instalação

Requer **Python 3.10 ou superior** (desenvolvido e testado em 3.13).

## Ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

## Dependências

São dois conjuntos independentes. A API e o notebook não compartilham bibliotecas, e cada um roda sem o outro — mas se você pretende usar os dois, instale ambos no mesmo ambiente virtual.

### API

```bash
pip install -r fastapi/requirements.txt
```

| Pacote | Uso |
|---|---|
| `fastapi` | framework da aplicação |
| `uvicorn[standard]` | servidor ASGI |
| `pydantic` | validação dos schemas de entrada e saída |
| `PyJWT` | emissão e verificação do token HS256 |
| `bcrypt` | verificação da senha contra o hash armazenado |
| `python-multipart` | leitura do formulário do `OAuth2PasswordRequestForm` |

### Notebook

```bash
pip install pandas numpy matplotlib seaborn scipy jupyter
```

`scipy` é usado nos testes de hipótese da seção 5.3 (qui-quadrado e Kolmogorov–Smirnov).

## Erro comum

Se `uvicorn` não for reconhecido como comando, o ambiente virtual está ativo mas as dependências da API não foram instaladas nele — só as do notebook. Rode `pip install -r fastapi/requirements.txt` e tente novamente.
