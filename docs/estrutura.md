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
│   ├── config.py                          parâmetros da API e do JWT
│   ├── requirements.txt
│   ├── models/                            schemas Pydantic de entrada e saída
│   │   ├── auth.py
│   │   ├── health.py
│   │   └── predict.py
│   ├── routes/                            definição dos endpoints
│   │   ├── auth.py
│   │   ├── health.py
│   │   └── predict.py
│   └── security/                          autenticação e emissão/validação de tokens
│       ├── auth.py
│       └── users.py
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
| `config.py` | Constantes da API e parâmetros do JWT (`SECRET_KEY`, algoritmo, expiração). |
| `models/` | Schemas Pydantic. Definem e validam o contrato de entrada e saída de cada rota. |
| `routes/` | Um módulo por área (`health`, `auth`, `predict`). O `__init__.py` agrega os roteadores em `api_router`. |
| `security/` | `OAuth2PasswordBearer`, verificação de senha, emissão e validação de token. `users.py` isola a base de usuários. |

As rotas não conhecem detalhes de criptografia e o módulo de segurança não conhece HTTP além das exceções que levanta — a dependência `get_current_user` é o único ponto de contato entre os dois.
