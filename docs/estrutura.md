# Estrutura do projeto

```
.
├── data/
│   └── customer_support_tickets.csv       dataset original (Kaggle)
├── docs/
│   ├── estrutura.md                       este arquivo
│   ├── dataset.md                         fonte, características e escolha do dataset
│   ├── instalacao.md                      pré-requisitos e ambiente virtual
│   ├── execucao.md                        como rodar a API e o notebook
│   ├── api.md                             endpoints, autenticação e exemplos
│   ├── seguranca.md                       DFD, trust boundaries e tríade CIA
│   └── eda.md                             conclusões e hipóteses da análise
├── eda/
│   └── eda_customer_support_tickets.ipynb análise exploratória completa
├── fastapi/
│   ├── main.py                            ponto de entrada da aplicação
│   ├── config.py                          parâmetros da API, do JWT e caminho do banco
│   ├── db.py                              engine e sessão SQLModel
│   ├── sqlite_database.py                 cria e popula o banco (sqlite3)
│   ├── database.db                        banco SQLite gerado pelo script acima
│   ├── requirements.txt
│   ├── models/                            schemas Pydantic e tabelas SQLModel
│   │   ├── auth.py
│   │   ├── health.py
│   │   ├── predict.py
│   │   └── tables.py
│   ├── routes/                            definição dos endpoints
│   │   ├── auth.py
│   │   ├── health.py
│   │   └── predict.py
│   ├── security/                          autenticação, headers de segurança e rate limit
│   │   ├── auth.py
│   │   ├── headers.py
│   │   └── rate_limit.py
│   └── tests/                             testes de ownership, headers/CORS e rate limit
│       ├── conftest.py
│       ├── test_ownership.py
│       └── test_security.py
├── others/
│   ├── dfd.png                            diagrama de fluxo de dados
│   └── dfd.mmd                            fonte Mermaid do diagrama
└── README.md
```

## Organização da aplicação

A aplicação segue a divisão modular exigida pelo enunciado, com uma responsabilidade por diretório.

| Diretório | Responsabilidade |
|---|---|
| `main.py` | Instancia o `FastAPI` e registra o roteador agregado. Nenhuma lógica de negócio. |
| `config.py` | Constantes da API, parâmetros do JWT (`SECRET_KEY`, algoritmo, expiração) e caminho do banco. |
| `db.py` | Engine SQLModel e a dependência `get_session`. Único ponto de acesso ao banco pela API. |
| `sqlite_database.py` | Script de linha de comando (`sqlite3`) que cria o schema e popula os dados iniciais. Não é importado pela API. |
| `models/` | Schemas Pydantic (contrato de entrada e saída) e, em `tables.py`, as tabelas SQLModel `users` e `predictions`. |
| `routes/` | Um módulo por área (`health`, `auth`, `predict`). O `__init__.py` agrega os roteadores em `api_router`. |
| `security/` | `OAuth2PasswordBearer`, verificação de senha contra o hash no banco, emissão e validação de token. `headers.py` é o middleware de headers de segurança e `rate_limit.py` o limiter do SlowAPI. |

As rotas não conhecem detalhes de criptografia e o módulo de segurança não conhece HTTP além das exceções que levanta — a dependência `get_current_user` é o único ponto de contato entre os dois.
