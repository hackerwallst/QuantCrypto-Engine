# QuantCrypto-Engine

Laboratório de **backtesting e pesquisa quantitativa** focado em criptomoedas, rodando em Python (Google Colab + Jupyter).

> 🎯 Objetivo: ter um ambiente onde o trader só pluga a estratégia (EMA, Fibonacci, etc.) e o engine cuida de **dados**, **backtest**, **métricas** e **gráficos**.

---

## 🔧 Status atual

- Projeto em **fase inicial (MVP)**.
- Lógica principal está sendo construída dentro da pasta `Framework/` em notebooks do Google Colab.
- Foco atual:
  - Baixar e organizar dados históricos.
  - Rodar backtests de forma consistente.
  - Gerar relatórios e gráficos para avaliar estratégias.

---

##  Como rodar no Google Colab

1. Abra um novo notebook no Google Colab.
2. Rode:

    ```python
    !git clone https://github.com/hackerwallst/QuantCrypto-Engine.git
    %cd QuantCrypto-Engine
    ```

3. Abra o notebook em `examples/Backtest_Framework_BTC.ipynb`.
4. Execute as células e analise os resultados.

