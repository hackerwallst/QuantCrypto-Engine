# framework/analytics_plots.py
# ------------------------------------------------------------
# Gráficos avançados (Equity, DD, histogramas, heatmaps, scatter)
# Estilo MT5 + StrategyQuant
# ------------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (16, 7)


# ----------------------------------------
# Helper seguro
# ----------------------------------------
def safe_float(x):
    try:
        return float(x)
    except:
        return np.nan


# ----------------------------------------
# EQUITY + DRAWDOWN
# ----------------------------------------
def plot_equity_and_dd(trades: pd.DataFrame):
    if trades is None or trades.empty:
        print("⚠ Nenhum trade para plotar.")
        return

    trades_sorted = trades.sort_values("exit_time")
    equity = trades_sorted["pnl"].cumsum()

    dd = equity - equity.cummax()
    dd_pct = dd / equity.cummax() * 100

    fig, ax = plt.subplots(2, 1, figsize=(18, 10), sharex=True)

    # Equity
    ax[0].plot(equity.values, color="blue", linewidth=2)
    ax[0].fill_between(np.arange(len(equity)), equity.values, color="blue", alpha=0.15)
    ax[0].set_title("Equity Curve (Saldo Acumulado)")
    ax[0].grid(True)

    # Drawdown
    ax[1].fill_between(np.arange(len(dd)), dd_pct.values, color="red", alpha=0.4)
    ax[1].plot(dd_pct.values, color="darkred", linewidth=1.5)
    ax[1].set_title("Drawdown (%)")
    ax[1].grid(True)

    plt.tight_layout()
    plt.show()


# ----------------------------------------
# HISTOGRAMAS: PnL, Risk:Reward, Duração
# ----------------------------------------
def plot_histograms(trades: pd.DataFrame):
    if trades is None or trades.empty:
        print("⚠ Nenhum trade para plotar.")
        return

    fig, ax = plt.subplots(1, 3, figsize=(24, 6))

    # PnL
    ax[0].hist(trades["pnl"], bins=40, color="gray")
    ax[0].set_title("Histograma de Lucro por Trade")

    # Risk:Reward
    if "risk" in trades.columns and trades["risk"].notna().any():
        rr = trades["pnl"] / trades["risk"].replace(0, np.nan)
    else:
        rr = np.zeros(len(trades))

    ax[1].hist(rr, bins=40, color="dodgerblue")
    ax[1].set_title("Histograma de Risk:Reward")

    # Duração
    if "duration" in trades.columns and trades["duration"].notna().any():
        dur = trades["duration"].dt.total_seconds() / 3600
    else:
        dur = np.zeros(len(trades))

    ax[2].hist(dur, bins=40, color="orange")
    ax[2].set_title("Duração dos Trades (Horas)")

    plt.tight_layout()
    plt.show()


# ----------------------------------------
# HEATMAP: Lucro por hora x dia da semana
# ----------------------------------------
def plot_trade_time_heatmap(trades: pd.DataFrame):
    if trades is None or trades.empty:
        print("⚠ Nenhum trade para plotar.")
        return

    trades = trades.copy()
    trades["hour"] = trades["entry_time"].dt.hour
    trades["dow"] = trades["entry_time"].dt.dayofweek

    pivot = trades.pivot_table(values="pnl", index="dow", columns="hour", aggfunc="mean")

    plt.figure(figsize=(18, 6))
    sns.heatmap(pivot, cmap="viridis", annot=False)
    plt.title("Heatmap: Lucro Médio por Horário")
    plt.ylabel("Dia da Semana (0=Seg)")
    plt.xlabel("Hora do Dia")
    plt.show()


# ----------------------------------------
# SCATTER RELATIONS (Max Favorável, Max Adverso, Duração)
# ----------------------------------------
def plot_scatter_relations(trades: pd.DataFrame):
    if trades is None or trades.empty:
        print("⚠ Nenhum trade para plotar.")
        return

    fig, ax = plt.subplots(1, 3, figsize=(26, 7))

    # Max Favorável
    ax[0].scatter(trades["max_favor"], trades["pnl"], alpha=0.6)
    ax[0].set_title("Max Favorável vs Lucro")

    # Max Adverso
    ax[1].scatter(trades["max_adverse"], trades["pnl"], alpha=0.6, color="red")
    ax[1].set_title("Max Adverso vs Lucro")

    # Duração
    if "duration" in trades.columns:
        dur = trades["duration"].dt.total_seconds() / 3600
    else:
        dur = np.zeros(len(trades))

    ax[2].scatter(dur, trades["pnl"], alpha=0.6, color="green")
    ax[2].set_title("Duração vs Lucro")

    plt.show()
