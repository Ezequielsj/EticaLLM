# EticaLLM

Experimento comparativo de julgamentos morais de modelos de linguagem usando
os 52 dilemas de *Moral judgment reloaded*.

## Arquivos principais

- `run_experiment.py`: coleta respostas do Gemini e retoma execuções interrompidas.
- `gemini_results.csv`: resultados válidos do Gemini.
- `copilot_results.csv`: resultados do segundo modelo.
- `RELATORIO_ANALISE_MORAL.md`: comparação e análise exploratória.

## Executar o Gemini

Configure a chave somente na sessão do PowerShell:

```powershell
$env:GEMINI_API_KEY="SUA_CHAVE"
py .\run_experiment.py --repetitions 2 --delay 8
```

Não coloque chaves de API em arquivos versionados.
