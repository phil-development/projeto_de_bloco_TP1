# Análise exploratória

Notebook completo: [`eda/eda_customer_support_tickets.ipynb`](../eda/eda_customer_support_tickets.ipynb)

## Etapas

| Seção | Conteúdo |
|---|---|
| 1 | Compreensão do problema e do dataset — fonte, características e motivo da escolha |
| 2 | Inspeção inicial — dimensões, tipos, amostra e estatísticas descritivas |
| 3 | Verificação da qualidade — nulos, duplicatas, cardinalidade, domínios e consistência temporal |
| 4 | Limpeza e preparação — remoção de PII, conversão de tipos, normalização do texto e features derivadas |
| 5 | Análise univariada — histogramas, boxplots e gráficos de frequência, com verificação estatística |
| 6 | Hipóteses sobre as intenções dos usuários |

## Principais conclusões

- **Os valores ausentes são estruturais.** Resolução, tempo de resolução e nota de satisfação só existem para os 32,7% de chamados fechados; a primeira resposta só existe para chamados que saíram de `Open`. Imputar esses campos introduziria informação falsa — eles permanecem nulos e são lidos como "evento ainda não ocorreu".
- **Dois campos temporais são inconsistentes.** Em cerca de metade dos chamados fechados a resolução antecede a primeira resposta, e todos os carimbos de atendimento caem numa janela de ~27 horas, embora as compras cubram 2020–2021. `First Response Time` e `Time to Resolution` foram descartados como features.
- **Nenhum metadado prediz a intenção.** Qui-quadrado de `Ticket Type` contra assunto, prioridade, canal e gênero devolve p > 0,45 em todos os casos; a idade é praticamente uniforme entre 18 e 70. O sinal precisa vir do texto.
- **O texto também não discrimina o rótulo.** Restringindo aos 15 modelos de frase mais frequentes (n = 4.438, teste bem condicionado), a abertura da descrição é independente tanto de `Ticket Subject` (p = 0,79) quanto de `Ticket Type` (p = 0,37).
- **PII é removida na preparação.** Nome e e-mail do cliente saem do DataFrame de trabalho por não terem valor preditivo e representarem risco desnecessário.

## Hipóteses

As quatro hipóteses estão desenvolvidas na seção 6 do notebook:

1. **A intenção não é inferível a partir dos metadados do chamado** — as cinco classes aparecem em proporções quase idênticas (19,3% a 20,7%) e nenhuma variável estruturada tem associação significativa com o alvo.
2. **A demanda é dominada por intenção técnica implícita** — os seis assuntos mais recorrentes são todos técnicos e somam 39,0% dos chamados (62,5% considerando os dez de natureza técnica), independentemente do tipo declarado.
3. **A intenção é expressa de forma curta, padronizada e centrada no produto** — mediana de 51 palavras, desvio de 8,6 e referência ao produto em 100% das descrições.
4. **A insatisfação não discrimina a intenção** — a nota de satisfação é quase uniforme entre 1 e 5 e existe apenas para chamados fechados; a prioridade também é uniforme e independente do tipo.

## Limitação registrada

A independência estatística observada é consistente com a natureza sintética do dataset: rótulos e metadados foram sorteados independentemente do texto. Isso não invalida o conjunto para o projeto — vocabulário, taxonomia e estrutura das mensagens são realistas — mas define uma expectativa honesta de desempenho e recomenda que, na etapa de modelagem, o alvo seja construído a partir do conteúdo textual em vez de usar `Ticket Type` cegamente.
