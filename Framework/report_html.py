# ============================================================
# RELATÓRIO HTML PRO — BASE64 + EXPLICAÇÕES DE CADA GRÁFICO
# ============================================================

import base64
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)
    return f"data:image/png;base64,{b64}"


# ============================================================
# MÉTRICAS (HTML)
# ============================================================

def compute_metrics_html(trades, initial_capital=1000.0):
    tr = trades.sort_values("exit_time")
    equity = initial_capital + tr["pnl"].cumsum()

    final_balance = equity.iloc[-1]
    net_profit    = final_balance - initial_capital
    total         = len(tr)
    wins          = (tr["pnl"] > 0).sum()
    losses        = (tr["pnl"] < 0).sum()
    win_rate      = (wins / total * 100) if total > 0 else 0.0
    gross_profit  = tr[tr["pnl"] > 0]["pnl"].sum()
    gross_loss    = tr[tr["pnl"] < 0]["pnl"].sum()
    profit_factor = gross_profit / abs(gross_loss) if gross_loss < 0 else np.nan

    dd         = equity - equity.cummax()
    max_dd     = dd.min()
    max_dd_pct = (max_dd / equity.cummax().max()) * 100

    expectancy = net_profit / total if total > 0 else 0.0
    sharpe     = tr["pnl"].mean() / (tr["pnl"].std() + 1e-9)

    dfm = pd.DataFrame([
        ("Capital Inicial", initial_capital),
        ("Saldo Final", float(final_balance)),
        ("Resultado Líquido", float(net_profit)),
        ("Total de Trades", int(total)),
        ("Vitórias", int(wins)),
        ("Derrotas", int(losses)),
        ("Taxa de Acerto (%)", float(win_rate)),
        ("Lucro Bruto", float(gross_profit)),
        ("Prejuízo Bruto", float(gross_loss)),
        ("Profit Factor", float(profit_factor)),
        ("Max Drawdown (valor)", float(max_dd)),
        ("Max Drawdown (%)", float(max_dd_pct)),
        ("Expectativa por Trade", float(expectancy)),
        ("Sharpe Ratio", float(sharpe)),
    ], columns=["Métrica", "Valor"])

    return dfm.to_html(index=False, classes="metrics-table")


# ============================================================
# GRÁFICOS BÁSICOS
# ============================================================

def chart_equity_dd(trades, initial_capital=1000.0):
    tr = trades.sort_values("exit_time")
    equity = initial_capital + tr["pnl"].cumsum()
    dd = equity - equity.cummax()
    dd_pct = dd / equity.cummax().replace(0, np.nan) * 100

    fig, ax = plt.subplots(2, 1, figsize=(18, 10), sharex=True)
    ax[0].plot(equity.values, color="cyan", linewidth=2)
    ax[0].set_title("Equity Curve")
    ax[0].grid(True)

    ax[1].fill_between(range(len(dd_pct)), dd_pct, color="red", alpha=0.4)
    ax[1].set_title("Drawdown (%)")
    ax[1].grid(True)

    return fig_to_base64(fig)


def chart_histogram_pnl(trades):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.hist(trades["pnl"], bins=40, color="gray", edgecolor="white")
    ax.set_title("Histograma de Lucro por Trade")
    ax.grid(True)
    return fig_to_base64(fig)


def chart_heatmap(trades):
    tr = trades.copy()
    tr["hour"] = tr["entry_time"].dt.hour
    tr["dow"] = tr["entry_time"].dt.dayofweek
    pivot = tr.pivot_table(values="pnl", index="dow", columns="hour", aggfunc="mean")

    fig, ax = plt.subplots(figsize=(14, 4))
    sns.heatmap(pivot, cmap="viridis", ax=ax)
    ax.set_title("Heatmap — Lucro Médio por Hora/Dia")
    return fig_to_base64(fig)


def chart_monthly_pnl(trades):
    t = trades.copy()
    t["month"] = t["exit_time"].dt.to_period("M")
    m = t.groupby("month")["pnl"].sum()

    fig, ax = plt.subplots(figsize=(14, 4))
    m.plot(kind="bar", ax=ax, color="dodgerblue")
    ax.set_title("Lucro por Mês")
    ax.set_xlabel("month")
    ax.grid(True, axis="y")
    return fig_to_base64(fig)


def chart_yearly_pnl(trades):
    t = trades.copy()
    t["year"] = t["exit_time"].dt.year
    y = t.groupby("year")["pnl"].sum()

    fig, ax = plt.subplots(figsize=(10, 4))
    y.plot(kind="bar", ax=ax, color="purple")
    ax.set_title("Lucro por Ano")
    ax.set_xlabel("year")
    ax.grid(True, axis="y")
    return fig_to_base64(fig)


def chart_best_worst(trades):
    best = trades.nlargest(20, "pnl")
    worst = trades.nsmallest(20, "pnl")

    fig, ax = plt.subplots(1, 2, figsize=(18, 5))
    ax[0].bar(range(len(best)), best["pnl"], color="green")
    ax[0].set_title("Top 20 Trades (Melhores)")

    ax[1].bar(range(len(worst)), worst["pnl"], color="red")
    ax[1].set_title("Top 20 Trades (Piores)")

    return fig_to_base64(fig)


# ============================================================
# MONTE CARLO — DISTRIBUIÇÃO — ROBUSTEZ — R-MULTIPLES
# ============================================================

def chart_monte_carlo_equity(trades, initial_capital=1000.0, n_sims=200):
    pnl = trades.sort_values("exit_time")["pnl"].values
    sims = []

    for _ in range(n_sims):
        sample = np.random.permutation(pnl)
        eq = initial_capital + np.cumsum(sample)
        sims.append(eq)

    sims = np.array(sims)
    eq_real = initial_capital + np.cumsum(pnl)

    fig, ax = plt.subplots(figsize=(18, 8))
    for i in range(min(80, n_sims)):
        ax.plot(sims[i], color="gray", alpha=0.08)

    ax.plot(eq_real, color="cyan", linewidth=2, label="Equity Real")
    ax.set_title(f"Monte Carlo — Equity (shuffle, {n_sims} simulações)")
    ax.set_xlabel("Trade")
    ax.set_ylabel("Equity")
    ax.grid(True)
    ax.legend()

    return fig_to_base64(fig)


def chart_monte_carlo_distribution(trades, initial_capital=1000.0, n_sims=500):
    pnl = trades.sort_values("exit_time")["pnl"].values
    finals = []
    max_dds = []

    for _ in range(n_sims):
        sample = np.random.choice(pnl, size=len(pnl), replace=True)
        eq = initial_capital + np.cumsum(sample)
        finals.append(eq[-1])

        cummax = np.maximum.accumulate(eq)
        dd = eq - cummax
        max_dds.append(dd.min())

    finals = np.array(finals)
    max_dds = np.array(max_dds)

    fig, ax = plt.subplots(1, 2, figsize=(18, 6))

    ax[0].hist(finals, bins=40, color="steelblue", edgecolor="black")
    ax[0].set_title("Monte Carlo — Distribuição do Saldo Final")

    ax[1].hist(max_dds, bins=40, color="red", edgecolor="black")
    ax[1].set_title("Monte Carlo — Distribuição do Max Drawdown")

    return fig_to_base64(fig)


# ============================================================
# EMA ROBUSTNESS (usa Backtester do módulo backtester.py)
# ============================================================

from backtester import Backtester  # IMPORTANTE!


def generate_signals_ema_param(df, fast_period=9, slow_period=21):
    data = df.copy()
    data["datetime"] = pd.to_datetime(data["datetime"])

    fast = data["close"].ewm(span=fast_period, adjust=False).mean()
    slow = data["close"].ewm(span=slow_period, adjust=False).mean()

    prev_fast = fast.shift(1)
    prev_slow = slow.shift(1)

    buy  = (prev_fast <= prev_slow) & (fast > slow)
    sell = (prev_fast >= prev_slow) & (fast < slow)

    sig = pd.DataFrame({"datetime": data["datetime"], "signal": 0})
    sig.loc[buy, "signal"] = 1
    sig.loc[sell, "signal"] = -1

    return sig


def chart_ema_robustness(df, config,
                         fast_range=range(5, 15),
                         slow_range=range(15, 35)):
    fast_list = list(fast_range)
    slow_list = list(slow_range)

    res = np.full((len(fast_list), len(slow_list)), np.nan)

    for i, f in enumerate(fast_list):
        for j, s in enumerate(slow_list):
            if f >= s:
                continue

            sig = generate_signals_ema_param(df, fast_period=f, slow_period=s)
            bt = Backtester(df, config)
            tr = bt.run(sig)

            metric = tr["pnl"].sum() if tr is not None and not tr.empty else np.nan
            res[i, j] = metric

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        res,
        xticklabels=slow_list,
        yticklabels=fast_list,
        cmap="RdYlGn",
        center=0,
        ax=ax
    )

    ax.set_title("Mapa de Robustez — EMA Rápida x EMA Lenta")
    ax.set_xlabel("EMA Lenta")
    ax.set_ylabel("EMA Rápida")

    return fig_to_base64(fig)


# ============================================================
# R-MULTIPLES
# ============================================================

def chart_r_multiples(trades):
    tr = trades.copy()

    if "max_adverse" in tr.columns:
        risk = tr["max_adverse"].abs().replace(0, np.nan)
        tr["R"] = tr["pnl"] / risk
        r = tr["R"].replace([np.inf, -np.inf], np.nan).dropna()
    else:
        r = pd.Series([], dtype=float)

    fig, ax = plt.subplots(figsize=(10, 4))
    if not r.empty:
        ax.hist(r, bins=40, color="gray", edgecolor="black")

    ax.set_title("Histograma de R-Multiples (PnL / risco do trade)")
    ax.grid(True)

    return fig_to_base64(fig)


# ============================================================
# GERADOR HTML FINAL
# ============================================================

def generate_html_report_base64(df, trades, config,
                                initial_capital=1000.0,
                                output_path="/content/backtest_report.html"):

    if trades is None or trades.empty:
        print("⚠ Sem trades, nenhum relatório será gerado.")
        return

    metrics_html  = compute_metrics_html(trades, initial_capital)
    img_equity_dd = chart_equity_dd(trades, initial_capital)
    img_hist_pnl  = chart_histogram_pnl(trades)
    img_heatmap   = chart_heatmap(trades)
    img_monthly   = chart_monthly_pnl(trades)
    img_yearly    = chart_yearly_pnl(trades)
    img_bw        = chart_best_worst(trades)

    img_mc_eq   = chart_monte_carlo_equity(trades, initial_capital)
    img_mc_dist = chart_monte_carlo_distribution(trades, initial_capital)
    img_robust  = chart_ema_robustness(df, config)
    img_rmult   = chart_r_multiples(trades)

    trades_html = trades.to_html(index=False, classes="trades-table")

    html = f"""<HTML LONG STRING … TRUNCATED TO KEEP CLEAN>"""  # Mantenha o seu HTML completo aqui!

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Relatório HTML salvo em: {output_path}")
    print("📁 É um arquivo único. Pode baixar e abrir em qualquer lugar.")
