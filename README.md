# Sistema de Atendimento ao Cliente com IA — TP1

Primeira entrega do Projeto de Bloco. O escopo desta etapa é definir o domínio do sistema: análise
exploratória do dataset de tickets de suporte e estrutura base da API FastAPI com autenticação JWT.

## Autores

- Caique Sanderson de Sá Borges
- Filipe Vasconcelos Vilarino
- João Victor Cicero de Miranda Teixeira Ramos
- José Augusto Nascimento Rosa Santos

## Documentação

| Documento | Conteúdo |
|---|---|
| [Estrutura do projeto](docs/estrutura.md) | Árvore de diretórios e organização modular da aplicação |
| [Dataset](docs/dataset.md) | Fonte, principais características e motivo da escolha |
| [Instalação](docs/instalacao.md) | Pré-requisitos, ambiente virtual e dependências |
| [Execução](docs/execucao.md) | Como subir a API e como rodar o notebook |
| [API](docs/api.md) | Endpoints, autenticação JWT, exemplos e respostas de erro |
| [Modelagem de ameaças](docs/seguranca.md) | DFD, fronteiras de confiança e tríade CIA por componente |
| [Análise exploratória](docs/eda.md) | Etapas, conclusões e hipóteses sobre as intenções |

## Início rápido

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r fastapi/requirements.txt

cd fastapi
uvicorn main:app --reload
```

Documentação interativa em `http://127.0.0.1:8000/docs`. Credenciais: `admin` / `Infnet@2025`.

## Escopo e limitações desta entrega

Esta é a primeira de várias entregas do bloco. Alguns pontos precisam ficar explícitos para que o estado do
projeto não seja lido como algo além do que é.

**A rota `/predict` não executa um modelo.** Ela devolve uma intenção fixa (`Technical issue`, confiança
`0.87`, `model_version: "stub-0.0.0"`) que simula a saída do classificador. O texto enviado é validado, mas
não é lido para decidir a resposta — qualquer entrada produz o mesmo retorno. É o comportamento pedido pelo
enunciado: a rota existe para fechar o contrato da API, a autenticação e a validação antes que o modelo
exista. O identificador `stub-0.0.0` sinaliza esse estado na própria resposta HTTP.

**A EDA e a API não se comunicam.** São artefatos independentes nesta etapa: o notebook não importa nada de
`fastapi/`, e a aplicação não lê o dataset. O único vínculo é conceitual — os cinco valores do enum `Intent`
correspondem exatamente às cinco categorias de `Ticket Type` identificadas na análise. A integração ocorre na
próxima entrega, quando um modelo treinado sobre esses dados for carregado pela rota.

**O dataset é sintético e seus rótulos são independentes do texto.** A análise verificou isso formalmente:
qui-quadrado de `Ticket Type` contra assunto, prioridade, canal e gênero devolve p > 0,45 em todos os casos, e
mesmo a frase de abertura da descrição é independente do rótulo (p = 0,79 no teste restrito aos 15 modelos de
frase mais frequentes). A consequência prática é que um classificador treinado diretamente sobre `Ticket Type`
tende a não superar o acaso. A limitação está registrada na seção 6 do notebook, junto com a recomendação de
derivar o alvo do conteúdo textual na etapa de modelagem.

**As decisões de segurança seguem o enunciado, não um cenário de produção.** As credenciais ficam no
código-fonte (com a senha armazenada apenas como hash bcrypt), `SECRET_KEY` tem valor de *fallback* em
`config.py` e o token não possui mecanismo de revogação. As três limitações estão documentadas em
[Modelagem de ameaças](docs/seguranca.md).

**O notebook é reexecutável.** Realiza uma única operação de I/O — a leitura do CSV — e nunca escreve em
disco. A limpeza da seção 4 opera sobre uma cópia em memória, de modo que o arquivo original permanece
inalterado.

## Requisitos do enunciado

| Requisito | Onde está atendido |
|---|---|
| Documentação técnica do dataset: fonte, características e motivo da escolha | [docs/dataset.md](docs/dataset.md) e seção 1 do notebook |
| EDA: compreensão do problema e do dataset | Seção 1 do notebook |
| EDA: inspeção inicial | Seção 2 do notebook |
| EDA: verificação da qualidade dos dados | Seção 3 do notebook |
| EDA: limpeza e preparação dos dados | Seção 4 do notebook |
| EDA: análise univariada com histogramas e gráficos | Seção 5 do notebook |
| Pelo menos 3 hipóteses sobre as intenções dos usuários | Seção 6 do notebook — são 4 |
| Projeto FastAPI modular executável com `uvicorn main:app --reload` | [fastapi/](fastapi/) e [docs/execucao.md](docs/execucao.md) |
| Arquivo `main`, diretórios `routes`, `models` e `security` | [docs/estrutura.md](docs/estrutura.md) |
| Rotas `GET /health`, `POST /auth/token` e `POST /predict` | [docs/api.md](docs/api.md) |
| Autenticação JWT com `OAuth2PasswordBearer` e usuário admin in-code | [fastapi/security/](fastapi/security/) e [docs/api.md](docs/api.md) |
| Rota `/predict` protegida por token válido | [fastapi/routes/predict.py](fastapi/routes/predict.py) |
| DFD com entradas, saídas e trust boundaries | [others/dfd.png](others/dfd.png) e [docs/seguranca.md](docs/seguranca.md) |
| Tríade CIA aplicada a cada componente | [docs/seguranca.md](docs/seguranca.md) |
| Estrutura do repositório: `data`, `eda`, `fastapi`, `others` | [docs/estrutura.md](docs/estrutura.md) |
