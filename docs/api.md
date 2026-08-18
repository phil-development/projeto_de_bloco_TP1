# API

## Endpoints

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| `GET` | `/health` | pública | Verifica se a API está ativa |
| `POST` | `/auth/token` | pública | Autentica o usuário e devolve um JWT |
| `POST` | `/predict` | Bearer JWT | Recebe o texto do ticket e devolve a intenção |

## Autenticação

O único usuário autorizado é definido em [`fastapi/security/users.py`](../fastapi/security/users.py). A senha não é armazenada em claro — apenas o seu hash bcrypt.

```
usuário: admin
senha:   Infnet@2025
```

`/auth/token` recebe as credenciais no formato `application/x-www-form-urlencoded`, conforme o padrão `OAuth2PasswordRequestForm`, e devolve um token HS256 com validade de 30 minutos.

`/predict` é protegida por `OAuth2PasswordBearer`. A dependência `get_current_user` decodifica o token, valida assinatura e expiração e confere que o `sub` corresponde ao usuário admin — qualquer falha resulta em `401`.

Em produção, `SECRET_KEY` deve vir da variável de ambiente de mesmo nome. O valor presente em `config.py` serve apenas ao ambiente local.

## A rota `/predict`

Nesta entrega a rota **não executa nenhum modelo**. Ela devolve uma intenção fixa que simula a saída do classificador que será implementado na próxima etapa:

```python
STUB_INTENT = Intent.TECHNICAL_ISSUE
STUB_CONFIDENCE = 0.87
STUB_MODEL_VERSION = "stub-0.0.0"
```

O texto enviado é validado, mas não é lido para decidir a resposta — qualquer entrada produz o mesmo retorno. O campo `model_version` explicita esse estado na própria resposta HTTP.

O que já é definitivo e permanecerá quando o modelo entrar: a exigência do token, a validação do corpo pelo Pydantic (texto entre 3 e 2000 caracteres, caso contrário `422`) e o formato da resposta.

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

## Respostas de erro

| Situação | Status |
|---|---|
| `/predict` sem cabeçalho `Authorization` | `401` |
| Token expirado, malformado ou com assinatura inválida | `401` |
| Usuário ou senha incorretos em `/auth/token` | `401` |
| Texto fora do intervalo de 3 a 2000 caracteres | `422` |
