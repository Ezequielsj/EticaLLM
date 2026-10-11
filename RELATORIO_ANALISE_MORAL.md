# Comparação de julgamentos morais por dois modelos de linguagem

## 1. Objetivo

Este relatório compara as respostas de dois modelos de linguagem aos 52
dilemas morais do estudo *Moral judgment reloaded: a moral dilemma validation
study*. Cada dilema foi apresentado duas vezes a cada modelo. O objetivo foi
avaliar a proporção de respostas utilitaristas e verificar se a característica
pessoal ou impessoal do dilema está associada à decisão.

Os resultados brutos estão em:

- [gemini_results.csv](./gemini_results.csv)
- [copilot_results.csv](./copilot_results.csv)

## 2. Hipótese

A hipótese principal foi:

> Dilemas pessoais produzirão uma proporção menor de respostas utilitaristas
> do que dilemas impessoais.

Foi adotada a codificação usada no experimento:

- `YES`: realização da ação descrita, classificada como utilitarista;
- `NO`: recusa da ação descrita, classificada como deontológica.

Essa codificação é operacional. Ela não significa que toda justificativa
utilitarista ou deontológica possa ser completamente reduzida à resposta
YES/NO.

## 3. Método

Foram analisados 52 dilemas, sendo 26 pessoais e 26 impessoais, com duas
execuções por dilema e por modelo. O prompt solicitava uma resposta no formato:

```text
DECISION: YES or NO
REASON: one brief sentence
```

No arquivo do Gemini, foram excluídos da análise os registros que continham
erros de API ou que não apresentavam uma decisão classificável. Isso é
necessário porque o arquivo contém tentativas que falharam por indisponibilidade,
limite de cota ou resposta sem o formato solicitado. A análise usa somente
104 respostas válidas do Gemini.

O arquivo do Copilot contém 104 respostas válidas. Essas respostas foram
produzidas nesta conversa e, portanto, não têm o mesmo grau de automatização e
independência do conjunto obtido por chamadas repetidas à API do Gemini.

## 4. Resultados descritivos

### 4.1 Resultado geral

| Modelo | Respostas válidas | Utilitaristas | Deontológicas | % utilitaristas |
|---|---:|---:|---:|---:|
| Gemini | 104 | 104 | 0 | 100,0% |
| Copilot | 104 | 52 | 52 | 50,0% |

### 4.2 Resultado por característica do dilema

| Modelo | Tipo | Respostas | Utilitaristas | Deontológicas | % utilitaristas |
|---|---|---:|---:|---:|---:|
| Gemini | Pessoal | 52 | 52 | 0 | 100,0% |
| Gemini | Impessoal | 52 | 52 | 0 | 100,0% |
| Copilot | Pessoal | 52 | 0 | 52 | 0,0% |
| Copilot | Impessoal | 52 | 52 | 0 | 100,0% |

No Gemini, não houve diferença observada entre dilemas pessoais e impessoais:
ambos produziram 100% de respostas utilitaristas. No Copilot, houve uma
separação completa: todas as respostas aos dilemas pessoais foram
deontológicas e todas as respostas aos dilemas impessoais foram utilitaristas.

### 4.3 Resultado por dilema

O Copilot apresentou o mesmo padrão em todos os 52 dilemas:

- dilemas pessoais: 0 de 2 respostas utilitaristas;
- dilemas impessoais: 2 de 2 respostas utilitaristas.

O Gemini apresentou duas respostas utilitaristas válidas em cada um dos 52
dilemas. Assim, não houve variação entre repetições ou entre os tipos de
dilema nesse conjunto.

## 5. Análise estatística exploratória

### 5.1 Associação entre tipo de dilema e decisão

Para o Copilot, a tabela de contingência foi:

|  | Utilitarista | Deontológica |
|---|---:|---:|
| Pessoal | 0 | 52 |
| Impessoal | 52 | 0 |

Essa é uma associação perfeita entre o tipo de dilema e a classificação da
resposta. Um teste exato de Fisher aplicado às 104 linhas produziria um
resultado extremamente significativo, com `p < 0,001`. O tamanho de efeito
descritivo também é máximo: a diferença entre as proporções utilitaristas é
de 100 pontos percentuais (0% contra 100%).

Para o Gemini, a tabela foi:

|  | Utilitarista | Deontológica |
|---|---:|---:|
| Pessoal | 52 | 0 |
| Impessoal | 52 | 0 |

Como não houve variação na classificação, não há evidência de associação entre
tipo de dilema e resposta dentro do conjunto do Gemini. A proporção foi 100%
em ambos os tipos.

### 5.2 Comparação entre modelos

Considerando todas as respostas válidas, o Gemini produziu 100% de respostas
utilitaristas e o Copilot produziu 50%. A diferença descritiva entre modelos
foi de 50 pontos percentuais.

Entretanto, essa comparação deve ser interpretada com cautela: as respostas
não são observações completamente independentes, pois cada modelo respondeu
aos mesmos 52 dilemas duas vezes. Além disso, o conjunto do Copilot foi
produzido em uma interação conversacional, e não por uma sequência
automatizada equivalente à do Gemini.

## 6. Interpretação

A hipótese foi **parcialmente apoiada**:

1. No Copilot, dilemas pessoais apresentaram menos respostas utilitaristas do
   que dilemas impessoais, exatamente como previsto.
2. No Gemini, a hipótese não foi confirmada nem refutada de forma informativa,
   porque todas as respostas foram classificadas como utilitaristas,
   independentemente do tipo de dilema.
3. Os modelos apresentaram perfis muito diferentes: o Gemini mostrou um padrão
   utilitarista constante, enquanto o Copilot mostrou sensibilidade máxima à
   distinção pessoal/impessoal.

O resultado do Gemini pode indicar uma preferência utilitarista do modelo,
mas também pode refletir o prompt, o modelo escolhido, a temperatura, a
interpretação da pergunta final ou a regra simplificada de classificação.
Portanto, não se deve concluir que o Gemini “é utilitarista” em sentido geral
com base somente neste experimento.

## 7. Limitações

1. **Independência das observações.** As duas respostas por dilema não são
   completamente independentes. Testes que tratam as 104 linhas como
   observações independentes podem subestimar a incerteza.
2. **Classificação binária.** A regra YES = utilitarista e NO = deontológica é
   uma operacionalização simplificada. Uma justificativa pode combinar
   elementos consequencialistas e deontológicos.
3. **Diferença entre os procedimentos.** O Gemini foi executado por API em
   chamadas repetidas. As respostas do Copilot foram produzidas nesta
   conversa, o que pode introduzir dependência de contexto e ausência de
   aleatoriedade comparável.
4. **Efeito teto do Gemini.** Como todas as respostas válidas do Gemini foram
   utilitaristas, não é possível estimar adequadamente uma diferença interna
   entre tipos de dilema nesse modelo.
5. **Registros de erro.** O arquivo do Gemini contém tentativas malsucedidas
   causadas por erros de rede, cota, permissões e respostas não classificáveis.
   Esses registros foram excluídos, não imputados.
6. **Generalização.** Os resultados se referem aos modelos, versões, prompts,
   parâmetros e momento de execução utilizados; não representam todas as
   versões desses sistemas.

## 8. Conclusão

Nos dados analisados, o Gemini apresentou 104 respostas utilitaristas em 104
respostas válidas. O Copilot apresentou 52 respostas utilitaristas e 52
deontológicas. A hipótese de que dilemas pessoais gerariam menos respostas
utilitaristas foi claramente observada no Copilot, mas não pôde ser avaliada
de modo discriminativo no Gemini devido ao padrão de 100% de respostas
utilitaristas.

A conclusão mais segura é que os dois sistemas exibiram padrões de resposta
distintos neste conjunto de dilemas. O estudo deve ser apresentado como uma
análise exploratória, e não como uma medição definitiva da orientação moral
dos modelos.

