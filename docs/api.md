# API

## Endpoints

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| `GET` | `/health` | pública | Verifica se a API está ativa |
| `POST` | `/auth/token` | pública | Autentica o usuário e devolve um JWT (limite de 10 requisições por minuto por cliente) |
| `POST` | `/predict` | Bearer JWT | Recebe o texto do ticket, devolve a intenção e grava a prediction em nome do usuário autenticado |
| `GET` | `/predictions` | Bearer JWT | Lista as predictions do usuário autenticado (`skip`, `limit` até 100) |
| `GET` | `/predictions/{id}` | Bearer JWT | Detalha uma prediction do usuário autenticado; `404` se não existir ou for de outro usuário |

## Banco de dados

Os usuários e as predictions ficam em SQLite (`fastapi/database.db`). O arquivo é criado e populado por
[`fastapi/sqlite_database.py`](../fastapi/sqlite_database.py), que usa apenas `sqlite3`; a API acessa o banco
somente via SQLModel (`db.py` e `models/tables.py`), sem SQL raw.

| Tabela | Colunas |
|---|---|
| `users` | `id`, `username` (único), `password_hash` (bcrypt), `role` (`admin` ou `user`), `created_at` |
| `predictions` | `id`, `owner_id` (FK → `users.id`), `text`, `intent`, `confidence`, `model_version`, `created_at` |

Dados iniciais: dois usuários e cinco predictions distribuídas entre eles (`model_version: "seed-fixture"`).

## Autenticação

As credenciais ficam na tabela `users`. A senha não é armazenada em claro — apenas o seu hash bcrypt.

| Usuário | Senha | Papel |
|---|---|---|
| `admin` | `Infnet@2025` | `admin` |
| `analista` | `Analista@2025` | `user` |

`/auth/token` recebe as credenciais no formato `application/x-www-form-urlencoded`, conforme o padrão `OAuth2PasswordRequestForm`, e devolve um token HS256 com validade de 30 minutos.

As rotas protegidas usam `OAuth2PasswordBearer`. A dependência `get_current_user` decodifica o token, valida assinatura e expiração e confirma no banco que o `sub` ainda corresponde a um usuário existente — qualquer falha resulta em `401`.

## Isolamento por dono

Cada prediction pertence a um usuário (`owner_id`). O dono é sempre o usuário do token, nunca um valor enviado no corpo da requisição (e `extra="forbid"` rejeita qualquer tentativa de enviá-lo). Isso protege contra BOLA (*Broken Object Level Authorization*, OWASP API1):

- `GET /predictions` filtra a consulta por `owner_id`.
- Toda rota que recebe o id de uma prediction depende de `get_owned_prediction` ([`routes/predict.py`](../fastapi/routes/predict.py)), que carrega o recurso e só o entrega se `owner_id` for o usuário autenticado.
- Id de outro usuário e id inexistente respondem igual (`404`), para não revelar quais ids existem. Usar `403` permitiria enumerar ids alheios.

Testes em [`fastapi/tests/test_ownership.py`](../fastapi/tests/test_ownership.py) (`python -m pytest tests`, de dentro de `fastapi/`; requer `pytest` e `httpx`).

Em produção, `SECRET_KEY` deve vir da variável de ambiente de mesmo nome. O valor presente em `config.py` serve apenas ao ambiente local.

## Headers de segurança

Um middleware ([`security/headers.py`](../fastapi/security/headers.py)) adiciona estes cabeçalhos a todas as respostas, inclusive às de erro (`401`, `422`, `429`):

| Header | Valor | Efeito |
|---|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | HSTS: o navegador passa a exigir HTTPS para o domínio (só tem efeito quando a API é servida por HTTPS) |
| `X-Frame-Options` | `DENY` | Impede que a API seja embutida em frames (clickjacking) |
| `X-Content-Type-Options` | `nosniff` | Impede o navegador de "adivinhar" o tipo do conteúdo |
| `Content-Security-Policy` | `default-src 'none'; frame-ancestors 'none'` | A API só devolve JSON, então nenhum recurso externo é permitido |

Exceção: `/docs` e `/redoc` usam uma CSP mais permissiva (CDN do Swagger UI/ReDoc e scripts inline), mas continuam com `frame-ancestors 'none'`. Em produção o ideal é desabilitar essas páginas.

## CORS

O `CORSMiddleware` aceita apenas as origens da allowlist `ALLOWED_ORIGINS` ([`config.py`](../fastapi/config.py)). O padrão é `http://localhost:3000` e `http://127.0.0.1:3000`; em outro ambiente, defina a variável de ambiente `ALLOWED_ORIGINS` com origens separadas por vírgula. Curinga (`*`) é recusado na inicialização.

- Métodos permitidos: `GET` e `POST`. Headers permitidos: `Authorization` e `Content-Type`.
- `allow_credentials=False`: o token vai no header `Authorization`, não em cookie.
- Origem fora da lista: a resposta não traz `Access-Control-Allow-Origin` (e o preflight devolve `400`).

## Rate limiting

`POST /auth/token` aceita no máximo **10 requisições por minuto por cliente** (identificado pelo IP de origem), usando SlowAPI. Passado o limite, a API devolve `429` com `Retry-After: 60` até a janela de 1 minuto se renovar. O limite conta tentativas com senha certa ou errada, para dificultar brute force. As demais rotas não têm limite.

O contador fica em memória, por processo: reiniciar a API o zera e, com vários processos, cada um conta separado. Atrás de um proxy reverso, o IP visto é o do proxy, a menos que ele repasse o IP real.

## A rota `/predict`

Nesta entrega a rota **não executa nenhum modelo**. Ela devolve uma intenção fixa que simula a saída do classificador que será implementado na próxima etapa:

```python
STUB_INTENT = Intent.TECHNICAL_ISSUE
STUB_CONFIDENCE = 0.87
STUB_MODEL_VERSION = "stub-0.0.0"
```

O texto enviado é validado, mas não é lido para decidir a resposta — qualquer entrada produz o mesmo retorno. O campo `model_version` explicita esse estado na própria resposta HTTP.

O que já é definitivo e permanecerá quando o modelo entrar: a exigência do token, a validação do corpo pelo Pydantic (texto entre 3 e 2000 caracteres, caso contrário `422`) e o formato da resposta. Cada chamada bem-sucedida também grava uma linha em `predictions` com o `owner_id` do chamador.

## Exemplos

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

```bash
curl http://127.0.0.1:8000/predictions -H "Authorization: Bearer $TOKEN"
```

## Respostas de erro

| Situação | Status |
|---|---|
| Rota protegida sem cabeçalho `Authorization` | `401` |
| `GET /predictions/{id}` com id inexistente ou de outro usuário | `404` |
| Token expirado, malformado ou com assinatura inválida | `401` |
| Usuário ou senha incorretos em `/auth/token` | `401` |
| Mais de 10 requisições por minuto a `/auth/token` pelo mesmo cliente | `429` |
| Texto fora do intervalo de 3 a 2000 caracteres | `422` |
| Corpo de `/predict` com campo não declarado (ex.: `owner_id`) | `422` |
