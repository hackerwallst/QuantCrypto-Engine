# framework/reporting.py
# ------------------------------------------------------------
# Funções de visualização e relatório do QuantCrypto Engine:
# - mostrar métricas em tabela
# - equity curve
# - drawdown curve
# ------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

from framework.metrics import performance_summary, compute_drawdown


# ------------------------------------------------------------
# TABELA DE MÉTRICAS
# ------------------------------------------------------------
def show_metrics(trades_df: pd.DataFrame, initial_cap: float):
    """
    Exibe tabela ordenada de métricas calculadas pelo performance_summary().
    """
    m = performance_summary(trades_df, initial_cap)

    order = [
        "initial_capital", "final_balance", "net_profit",
        "trades", "wins", "losses", "win_rate_pct",
        "gross_profit", "gross_loss", "profit_factor",
        "max_drawdown_pct",
    ]

    labels = {
        "initial_capital":  "Capital Inicial",
        "final_balance":    "Saldo Final",
        "net_profit":       "Resultado Líquido",
        "trades":           "Nº de Trades",
        "wins":             "Vitórias",
        "losses":           "Derrotas",
        "win_rate_pct":     "Taxa de Acerto (%)",
        "gross_profit":     "Lucro Bruto",
        "gross_loss":       "Prejuízo Bruto",
        "profit_factor":    "Profit Factor",
        "max_drawdown_pct": "Max Drawdown (%)",
    }

    df = pd.DataFrame({
        "Métrica": [labels[k] for k in order],
        "Valor":   [m[k] for k in order],
    })

    display(df)


# ------------------------------------------------------------
# EQUITY CURVE
# ------------------------------------------------------------
def plot_equity(trades_df: pd.DataFrame, initial_cap: float):
    """
    Plota curva de equity com base no PnL cumulativo.
    """
    if trades_df.empty:
        print("Sem trades para plotar equity.")
        return

    eq = initial_cap + trades_df["pnl"].cumsum()

    plt.figure(figsize=(10, 4))
    plt.plot(eq.values)
    plt.title("Equity Curve")
    plt.xlabel("Trade #")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.show()


# ------------------------------------------------------------
# DRAWDOWN CURVE
# ------------------------------------------------------------
def plot_drawdown(trades_df: pd.DataFrame, initial_cap: float):
    """
    Plota drawdown percentual da curva de equity.
    """
    if trades_df.empty:
        print("Sem trades para plotar drawdown.")
        return

    eq = initial_cap + trades_df["pnl"].cumsum()
    dd = compute_drawdown(eq)["drawdown"] * 100.0

    plt.figure(figsize=(10, 4))
    plt.plot(dd.values)
    plt.title("Drawdown (%)")
    plt.xlabel("Trade #")
    plt.ylabel("Drawdown (%)")
    plt.grid(True)
    plt.show()
