# framework/trade_plot.py
# ------------------------------------------------------------
# Plot avançado estilo MT5 para visualizar um trade específico.
# - Sorteia 1 trade
# - Centraliza janela
# - Exibe SL/TP, entrada/saída, indicadores
# - Candles + volume
# ------------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_trade_exemplar(df: pd.DataFrame,
                        trades: pd.DataFrame,
                        indicadores_da_estrategia=None,
                        janela_total: int = 200):
    """
    Plota um trade exemplar (sorteado aleatoriamente) com:
    - candles
    - SL / TP
    - entrada / saída com setas
    - indicadores da estratégia
    - volume

    parâmetros:
        df: DataFrame de candles
        trades: DataFrame de trades já fechado
        indicadores_da_estrategia: lista de nomes de colunas de indicadores
        janela_total: quantidade total de candles da janela
    """
    if trades is None or trades.empty:
        print("⚠ Não há trades para mostrar.")
        return

    if indicadores_da_estrategia is None:
        indicadores_da_estrategia = []

    # --------- SORTEAR TRADE ---------
    trade = trades.sample(1).iloc[0]
    entry_time = pd.to_datetime(trade["entry_time"])
    exit_time = pd.to_datetime(trade["exit_time"])
    entry_px = trade["entry_price"]
    exit_px = trade["exit_price"]
    direction = trade["direction"]

    print("\n===== TRADE EXEMPLAR =====")
    print("Direção:", direction)
    print("Entrada:", entry_time, "@", entry_px)
    print("Saída:", exit_time, "@", exit_px)

    # --------- PREPARAR DF ---------
    df2 = df.copy()
    df2["dt"] = pd.to_datetime(df2["datetime"])
    df2 = df2.set_index("dt")

    if entry_time not in df2.index or exit_time not in df2.index:
        print("⚠ Trade fora do histórico.")
        return

    entry_i = df2.index.get_loc(entry_time)
    exit_i = df2.index.get_loc(exit_time)

    # --------- JANELA CENTRALIZADA ---------
    duracao = exit_i - entry_i
    padding = max((janela_total - duracao) // 2, 20)

    start_i = max(0, entry_i - padding)
    end_i = min(len(df2) - 1, exit_i + padding)

    win = df2.iloc[start_i:end_i + 1].reset_index(drop=True)

    opens = win["open"].values
    highs = win["high"].values
    lows = win["low"].values
    closes = win["close"].values
    volume = win["volume"].values

    x = np.arange(len(win))

    up = closes >= opens
    down = closes < opens

    # FIGURA
    fig = plt.figure(figsize=(19, 12))
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1])
    ax = fig.add_subplot(gs[0])
    axv = fig.add_subplot(gs[1], sharex=ax)

    # --------- CANDLES ---------
    ax.vlines(x[up], lows[up], highs[up], color="green", linewidth=0.6)
    ax.vlines(x[down], lows[down], highs[down], color="red", linewidth=0.6)

    ax.vlines(x[up], opens[up], closes[up], color="green", linewidth=2.1)
    ax.vlines(x[down], opens[down], closes[down], color="red", linewidth=2.1)

    # --------- INDICADORES ---------
    for ind in indicadores_da_estrategia:
        if ind in win.columns:
            ax.plot(x, win[ind].values, linewidth=1.8, label=ind)

    if indicadores_da_estrategia:
        ax.legend(loc="upper left")

    # --------- SETAS DE ENTRY/EXIT ---------
    px_min = win["low"].min()
    px_max = win["high"].max()
    offset = (px_max - px_min) * 0.015

    entry_local = entry_i - start_i
    exit_local = exit_i - start_i

    if direction == "long":
        entry_y = win["low"].iloc[entry_local] - offset
        exit_y = win["high"].iloc[exit_local] + offset

        ax.scatter(entry_local, entry_y, s=260, color="lime",
                   edgecolor="black", marker="^", zorder=5)
        ax.scatter(exit_local, exit_y, s=260, color="yellow",
                   edgecolor="black", marker="v", zorder=5)

    else:
        entry_y = win["high"].iloc[entry_local] + offset
        exit_y = win["low"].iloc[exit_local] - offset

        ax.scatter(entry_local, entry_y, s=260, color="red",
                   edgecolor="black", marker="v", zorder=5)
        ax.scatter(exit_local, exit_y, s=260, color="purple",
                   edgecolor="black", marker="^", zorder=5)

    # --------- SL / TP ---------
    sl = trade.get("stop_price", None)
    tp = trade.get("take_price", None)

    ax.hlines(entry_px, 0, len(win) - 1, colors="blue",
              linestyles="--", linewidth=1.2, label="Entrada")

    if sl is not None and not pd.isna(sl):
        ax.hlines(sl, 0, len(win) - 1, colors="red",
                  linestyles="--", linewidth=1.4, label="Stop Loss")

    if tp is not None and not pd.isna(tp):
        ax.hlines(tp, 0, len(win) - 1, colors="green",
                  linestyles="--", linewidth=1.4, label="Take Profit")

    # Conexão entrada → saída
    ax.plot(
        [entry_local, exit_local],
        [entry_y, exit_y],
        linestyle="--",
        linewidth=1.3,
        color="gray",
    )

    # --------- LAYOUT ---------
    ax.set_title("Trade Exemplar — Backtest Visual", fontsize=17)
    ax.set_ylabel("Preço")
    ax.grid(False)

    axv.bar(x, volume, color="gray", width=1)
    axv.set_ylabel("Volume")
    axv.grid(False)

    plt.tight_layout()
    plt.show()
