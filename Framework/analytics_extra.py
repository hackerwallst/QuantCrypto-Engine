# framework/analytics_extra.py
# ------------------------------------------------------------
# Gráficos avançados (3D, sazonais, estatísticos)
# Complemento do analytics_plots.py
# ------------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (16, 7)


# ------------------------------------------------------------
# 3D — Close × Volume × ATR
# ------------------------------------------------------------
def plot_3d_atr_volume_price(df):
    """
    Scatter 3D mostrando Close × Volume × ATR.
    ATR detectado automaticamente.
    """
    atr_col = next((c for c in df.columns if "atr" in c.lower()), None)
    if atr_col is None:
        raise ValueError("Nenhuma coluna ATR foi encontrada no DataFrame.")

    print(f"[INFO] Usando coluna ATR: {atr_col}")

    xs = df["close"].astype(float)
    ys = df["volume"].astype(float)
    zs = df[atr_col].astype(float)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(xs, ys, zs, s=5, c=zs, cmap="viridis")
    ax.set_xlabel("Close")
    ax.set_ylabel("Volume")
    ax.set_zlabel(atr_col.upper())
    ax.set_title("Scatter 3D — Close × Volume × ATR")

    plt.show()


# ------------------------------------------------------------
# Lucro mensal
# ------------------------------------------------------------
def plot_monthly_profit(trades):
    trades = trades.copy()
    trades["month"] = trades["exit_time"].dt.to_period("M")

    month_pnl = trades.groupby("month")["pnl"].sum()

    plt.figure(figsize=(20, 6))
    month_pnl.plot(kind="bar", color="steelblue")
    plt.title("Lucro Acumulado por Mês")
    plt.ylabel("PnL")
    plt.grid(True, axis="y")
    plt.show()


# ------------------------------------------------------------
# Profit Factor mensal
# ------------------------------------------------------------
def plot_profit_factor_by_month(trades):
    trades = trades.copy()
    trades["month"] = trades["exit_time"].dt.to_period("M")

    def pf_calc(x):
        gp = x[x["pnl"] > 0]["pnl"].sum()
        gl = abs(x[x["pnl"] < 0]["pnl"].sum())
        return gp / gl if gl > 0 else np.nan

    pf = trades.groupby("month").apply(pf_calc)

    plt.figure(figsize=(20, 6))
    pf.plot(kind="bar", color="orange")
    plt.title("Profit Factor por Mês")
    plt.ylabel("Profit Factor")
    plt.grid(True, axis="y")
    plt.show()


# ------------------------------------------------------------
# Lucro anual
# ------------------------------------------------------------
def plot_yearly_profit(trades):
    trades = trades.copy()
    trades["year"] = trades["exit_time"].dt.year

    pnl = trades.groupby("year")["pnl"].sum()

    plt.figure(figsize=(14, 6))
    pnl.plot(kind="bar", color="purple")
    plt.title("Lucro Total por Ano")
    plt.ylabel("PnL")
    plt.grid(True, axis="y")
    plt.show()


# ------------------------------------------------------------
# Best & Worst trades
# ------------------------------------------------------------
def plot_best_and_worst_trades(trades, top=20):
    best = trades.nlargest(top, "pnl")
    worst = trades.nsmallest(top, "pnl")

    fig, ax = plt.subplots(1, 2, figsize=(26, 7))

    ax[0].bar(range(len(best)), best["pnl"], color="green")
    ax[0].set_title(f"Top {top} Trades (Melhores)")

    ax[1].bar(range(len(worst)), worst["pnl"], color="red")
    ax[1].set_title(f"Top {top} Trades (Piores)")

    plt.show()


# ------------------------------------------------------------
# Volatilidade × PnL
# ------------------------------------------------------------
def plot_volatility_vs_pnl(df, trades):
    vol = (df["high"] - df["low"]).astype(float)

    # alinhar tamanhos caso o dataset tenha mais candles que trades
    n = min(len(vol), len(trades))
    vol = vol[:n]
    pnl = trades["pnl"].iloc[:n]

    plt.figure(figsize=(14, 6))
    plt.scatter(vol, pnl, alpha=0.5)
    plt.title("Volatilidade × Lucro")
    plt.xlabel("High - Low")
    plt.ylabel("PnL")
    plt.grid(True)
    plt.show()


# ------------------------------------------------------------
# Boxplot por dia da semana
# ------------------------------------------------------------
def plot_boxplot_weekday(trades):
    trades = trades.copy()
    trades["weekday"] = trades["exit_time"].dt.dayofweek

    plt.figure(figsize=(14, 6))
    sns.boxplot(data=trades, x="weekday", y="pnl")
    plt.title("Distribuição de Lucro por Dia da Semana")
    plt.xlabel("Dia da Semana (0=Segunda)")
    plt.grid(True)
    plt.show()


# ------------------------------------------------------------
# Boxplot por hora do dia
# ------------------------------------------------------------
def plot_boxplot_hour(trades):
    trades = trades.copy()
    trades["hour"] = trades["exit_time"].dt.hour

    plt.figure(figsize=(14, 6))
    sns.boxplot(data=trades, x="hour", y="pnl")
    plt.title("Distribuição de Lucro por Hora do Dia")
    plt.xlabel("Hora do Dia")
    plt.grid(True)
    plt.show()


# ------------------------------------------------------------
# DASHBOARD COMPLETO
# ------------------------------------------------------------
def full_dashboard(df, trades):
    """
    Executa todos os gráficos avançados de forma organizada.
    """
    print("===== SCATTER 3D =====")
    plot_3d_atr_volume_price(df)

    print("===== LUCRO POR MÊS =====")
    plot_monthly_profit(trades)

    print("===== PROFIT FACTOR POR MÊS =====")
    plot_profit_factor_by_month(trades)

    print("===== LUCRO POR ANO =====")
    plot_yearly_profit(trades)

    print("===== BEST & WORST =====")
    plot_best_and_worst_trades(trades)

    print("===== VOLATILIDADE × PNL =====")
    plot_volatility_vs_pnl(df, trades)

    print("===== BOXPLOT SEMANAL =====")
    plot_boxplot_weekday(trades)

    print("===== BOXPLOT HORÁRIO =====")
    plot_boxplot_hour(trades)
