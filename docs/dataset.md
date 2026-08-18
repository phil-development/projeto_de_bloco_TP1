# Dataset

## Fonte

| Item | Descrição |
|---|---|
| Nome | Customer Support Ticket Dataset |
| Autor | Suraj Jha (`suraj520`) |
| Origem | https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset/data |
| Licença | CC0 1.0 (domínio público) |
| Arquivo | `data/customer_support_tickets.csv` |
| Natureza | Dados **sintéticos**, gerados artificialmente para fins didáticos |

## Principais características

São 8.469 registros e 17 colunas, um registro por chamado de suporte.

| Grupo | Colunas |
|---|---|
| Identificação e perfil | `Ticket ID`, `Customer Name`, `Customer Email`, `Customer Age`, `Customer Gender` |
| Produto | `Product Purchased` (42 produtos), `Date of Purchase` |
| Classificação | `Ticket Type` (5 classes), `Ticket Subject` (16), `Ticket Priority` (4), `Ticket Channel` (4) |
| Texto livre | `Ticket Description` — única variável de conteúdo, insumo do modelo de NLP |
| Ciclo de vida | `Ticket Status`, `Resolution`, `First Response Time`, `Time to Resolution`, `Customer Satisfaction Rating` |

`Ticket Type` é o alvo natural do classificador de intenção: **Technical issue**, **Billing inquiry**, **Cancellation request**, **Product inquiry** e **Refund request** — os mesmos cinco valores expostos pelo enum `Intent` da API.

## Motivo da escolha

1. **Aderência ao domínio.** É um dataset de tickets de suporte com texto livre e uma taxonomia de intenções pronta, exatamente o par entrada/saída da rota `/predict`.
2. **Riqueza de tipos.** Combina texto, categóricas, numéricas e temporais, permitindo exercitar todas as etapas da EDA em um único conjunto.
3. **Ausência de risco de privacidade.** Sendo sintético e licenciado como CC0, pode ser versionado em repositório público. Ainda assim ele *simula* PII (nome, e-mail), o que permite tratar a proteção desses campos como requisito de projeto.
4. **Volume adequado.** ~8,5 mil registros: suficiente para treinar e validar um classificador nas próximas entregas e leve o bastante para iteração rápida.

A documentação completa da fonte está na seção 1 do [notebook de EDA](../eda/eda_customer_support_tickets.ipynb).
