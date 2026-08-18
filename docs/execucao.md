# Execução

## API

O `main.py` fica na raiz de `fastapi/`, então o servidor precisa subir **de dentro dessa pasta**:

```bash
cd fastapi
uvicorn main:app --reload
```

- Aplicação: `http://127.0.0.1:8000`
- Documentação interativa (Swagger): `http://127.0.0.1:8000/docs`

Não execute `uvicorn fastapi.main:app` a partir da raiz do projeto: o diretório `fastapi/` tem o mesmo nome da biblioteca instalada e o Python tentaria importar a pasta no lugar do pacote, resultando em erro de importação.

## EDA

```bash
jupyter notebook eda/eda_customer_support_tickets.ipynb
```

O notebook é **idempotente** e pode ser reexecutado quantas vezes for necessário. Ele realiza uma única operação de I/O — o `pd.read_csv` da célula inicial — e nunca escreve em disco. A limpeza da seção 4 opera sobre uma cópia em memória (`dados = df.drop(...).copy()`), de modo que o CSV original permanece inalterado byte a byte e o DataFrame bruto continua disponível na sessão para comparação.
