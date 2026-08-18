# Sistema de Atendimento ao Cliente com IA — TP1

Primeira entrega do Projeto de Bloco. O escopo desta etapa é definir o domínio do sistema: análise
exploratória do dataset de tickets de suporte e estrutura base da API FastAPI com autenticação JWT.

O modelo de machine learning e o agente de IA serão implementados nas entregas seguintes — a rota
`/predict` já existe, mas devolve uma intenção fixa que simula a saída do classificador.

## Estrutura de pastas

```
.
├── data/
│   └── customer_support_tickets.csv       dataset original (Kaggle)
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

## Dataset

[Customer Support Ticket Dataset](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset/data)
(Kaggle, autor `suraj520`, licença CC0). São 8.469 chamados sintéticos com 17 colunas, cobrindo perfil do
cliente, produto, texto livre do chamado, classificação (`Ticket Type`, `Ticket Subject`, `Ticket Priority`,
`Ticket Channel`) e desfecho do atendimento.

A documentação da fonte, as características e a justificativa da escolha estão detalhadas na seção 1 do
notebook de EDA.

## Instalação

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r fastapi/requirements.txt
```

Para executar o notebook, instale também as dependências de análise:

```bash
pip install pandas numpy matplotlib seaborn scipy jupyter
```

## Execução

### API

```bash
cd fastapi
uvicorn main:app --reload
```

Documentação interativa em `http://127.0.0.1:8000/docs`.

### EDA

```bash
jupyter notebook eda/eda_customer_support_tickets.ipynb
```

## Endpoints

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| `GET` | `/health` | pública | Verifica se a API está ativa |
| `POST` | `/auth/token` | pública | Autentica o usuário e devolve um JWT |
| `POST` | `/predict` | Bearer JWT | Recebe o texto do ticket e devolve a intenção |

### Autenticação

O único usuário autorizado é definido em `fastapi/security/users.py`. A senha não é armazenada em claro —
apenas o seu hash bcrypt.

```
usuário: admin
senha:   Infnet@2025
```

`/auth/token` recebe as credenciais no formato `application/x-www-form-urlencoded` (padrão
`OAuth2PasswordRequestForm`) e devolve um token HS256 com validade de 30 minutos. `/predict` é protegida por
`OAuth2PasswordBearer` e responde `401` sem um token válido.

Em produção, `SECRET_KEY` deve ser fornecida pela variável de ambiente de mesmo nome; o valor presente em
`config.py` serve apenas ao ambiente local.

### Exemplos

```bash
curl http://127.0.0.1:8000/health

TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/token \
  -d "username=admin&password=Infnet@2025" | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -X POST http://127.0.0.1:8000/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"My laptop stopped charging after the last update."}'
```

```json
{ "intent": "Technical issue", "confidence": 0.87, "model_version": "stub-0.0.0" }
```

## Modelagem de ameaças

O diagrama de fluxo de dados está em [others/dfd.png](others/dfd.png), gerado a partir de
[others/dfd.mmd](others/dfd.mmd). Ele identifica duas fronteiras de confiança:

- **TB1 — borda de rede.** Separa a Internet do processo da aplicação. Todo tráfego que a atravessa carrega
  credenciais, token ou dado do cliente e depende de TLS.
- **TB2 — processo FastAPI/uvicorn.** Delimita a zona confiável onde residem os depósitos de dados. Nenhum
  segredo (`D1`, `D2`) atravessa TB1 de volta ao cliente.

### Tríade CIA por componente

| Componente | Confidencialidade | Integridade | Disponibilidade |
|---|---|---|---|
| Credenciais em trânsito (`POST /auth/token`) | Crítica — trafegam apenas sob TLS e nunca são registradas em log | Crítica — adulteração permite login indevido | Média — falha impede a emissão de novas sessões |
| `D1` — hash bcrypt do admin | Crítica — expõe a senha a ataque offline de dicionário | Crítica — substituir o hash concede acesso ao atacante | Alta — sem ele nenhum login é possível |
| `D2` — `SECRET_KEY` | Crítica — permite forjar JWT válido para qualquer usuário | Crítica — troca indevida invalida todos os tokens em uso | Alta — sem ela a API não autentica nem valida tokens |
| Token JWT emitido | Alta — o portador obtém acesso integral a `/predict` | Crítica — a assinatura HS256 impede alteração de `sub` e `exp` | Média — a expiração de 30 min é limite deliberado |
| `P4` — `POST /predict` | Média — a resposta revela o comportamento do modelo | Alta — a intenção retornada orienta o roteamento do chamado | Alta — é a função de negócio da aplicação |
| Texto do ticket (entrada) | Alta — pode conter dados pessoais informados no relato | Alta — texto truncado ou alterado produz classificação errada | Média — a requisição pode ser reenviada pelo cliente |
| `D3` — modelo de intenção | Média — os artefatos do modelo são ativo interno | Crítica — modelo adulterado enviesa todo o atendimento | Alta — indisponibilidade derruba a rota `/predict` |
| `P1` — `GET /health` | Baixa — não expõe dado sensível nem versões de dependências | Média — status falso-positivo mascara um incidente | Alta — é a base do monitoramento externo |

## Principais conclusões da EDA

- Os valores ausentes são **estruturais**: resolução, tempo de resolução e nota de satisfação só existem para
  os 32,7% de chamados fechados. Não devem ser imputados.
- `First Response Time` e `Time to Resolution` são inconsistentes (em metade dos casos a resolução antecede a
  primeira resposta) e foram descartados como features.
- Nenhum metadado — prioridade, canal, assunto, produto, idade, gênero — tem associação estatisticamente
  significativa com `Ticket Type` (qui-quadrado, todos os p > 0,45). O sinal da intenção precisa vir do texto.
- Nome e e-mail do cliente são removidos já na etapa de preparação, por serem PII sem valor preditivo.

As quatro hipóteses sobre a intenção dos usuários estão na seção 6 do notebook.
