# framework/advanced_metrics.py
# ------------------------------------------------------------
# Métricas avançadas estilo MT5 + métricas quant:
# - Profit factor, expectancy, média de ganhos/perdas
# - Sharpe por trade
# - Drawdown e recuperação
# - Retorno anualizado
# - Duração média
# ------------------------------------------------------------

import numpy as np
import pandas as pd
from IPython.display import display


def advanced_metrics_table(trades: pd.DataFrame, initial_capital: float):
    """
    Retorna e exibe um DataFrame com métricas avançadas da estratégia.
    """

    if trades is None or not isinstance(trades, pd.DataFrame) or trades.empty:
        print("⚠ Não há trades suficientes para calcular métricas.")
        return pd.DataFrame()

    df = trades.copy()

    if "pnl" not in df.columns:
        print("⚠ Coluna 'pnl' não encontrada.")
        return pd.DataFrame()

    # Ordenação
    if "exit_time" in df.columns:
        df = df.sort_values("exit_time").reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)

    total_trades = len(df)
    wins = df[df["pnl"] > 0]
    losses = df[df["pnl"] < 0]

    n_wins = len(wins)
    n_losses = len(losses)

    gross_profit = wins["pnl"].sum() if n_wins > 0 else 0.0
    gross_loss = losses["pnl"].sum() if n_losses > 0 else 0.0
    net_profit = df["pnl"].sum()
    final_balance = initial_capital + net_profit

    win_rate = (n_wins / total_trades * 100) if total_trades > 0 else np.nan
    profit_factor = (gross_profit / abs(gross_loss)) if gross_loss < 0 else np.nan

    avg_gain = wins["pnl"].mean() if n_wins > 0 else np.nan
    avg_loss = losses["pnl"].mean() if n_losses > 0 else np.nan
    expectancy = net_profit / total_trades if total_trades > 0 else np.nan

    # Equity & DD
    eq = initial_capital + df["pnl"].cumsum()
    peak = eq.cummax()
    dd = eq - peak
    dd_pct = dd / peak * 100

    max_dd = dd.min() if len(dd) else np.nan
    max_dd_pct = dd_pct.min() if len(dd_pct) else np.nan

    # Recuperação do DD
    recovery_trades = np.nan
    if len(dd_pct) > 0:
        dd_idx = dd_pct.idxmin()
        after = eq[dd_idx:]
        new_high_idx = after.idxmax()
        if eq[new_high_idx] >= peak.iloc[:dd_idx + 1].max():
            recovery_trades = int(new_high_idx - dd_idx)

    # Duração / retorno anualizado
    avg_duration = np.nan
    annual_return_pct = np.nan

    if "entry_time" in df.columns and "exit_time" in df.columns:
        entry = pd.to_datetime(df["entry_time"])
        exit_ = pd.to_datetime(df["exit_time"])
        durations = exit_ - entry
        avg_duration = durations.mean()

        start = entry.min()
        end = exit_.max()
        total_days = (end - start).days

        if total_days > 0:
            final_balance = eq.iloc[-1]
            annual_return = (final_balance / initial_capital) ** (365 / total_days) - 1
            annual_return_pct = annual_return * 100

    # Sharpe por trade
    returns = df["pnl"] / initial_capital
    sharpe = (returns.mean() / returns.std() * np.sqrt(total_trades)) if returns.std() > 0 else np.nan

    # Monta tabela
    metrics = {
        "Capital Inicial": initial_capital,
        "Saldo Final": final_balance,
        "Total de Trades": total_trades,
        "Número de Trades Vencedores": n_wins,
        "Número de Trades Perdedores": n_losses,
        "Taxa de Acerto (%)": win_rate,
        "Lucro Bruto": gross_profit,
        "Prejuízo Bruto": gross_loss,
        "Lucro Líquido": net_profit,
        "Fator de Lucro (Profit Factor)": profit_factor,
        "Média de Ganhos": avg_gain,
        "Média de Perdas": avg_loss,
        "Expectativa por Trade": expectancy,
        "Max Drawdown (valor)": max_dd,
        "Max Drawdown (%)": max_dd_pct,
        "Trades para Recuperar DD": recovery_trades,
        "Tempo Médio em Posição": avg_duration,
        "Taxa de Retorno Anualizada (%)": annual_return_pct,
        "Sharpe Ratio (por trade)": sharpe,
    }

    rows = []
    for k, v in metrics.items():
        if isinstance(v, (float, int, np.floating)):
            rows.append([k, None if pd.isna(v) else round(float(v), 4)])
        else:
            rows.append([k, v])

    table = pd.DataFrame(rows, columns=["Métrica", "Valor"])

    display(table)
    return table
