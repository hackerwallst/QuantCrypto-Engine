# framework/metrics.py
# ----------------------------------------------------
# Métricas principais para análise de performance:
# - equity curve
# - drawdown
# - summary de performance
# ----------------------------------------------------

import numpy as np
import pandas as pd


# ----------------------------------------------------
# EQUITY CURVE
# ----------------------------------------------------
def equity_curve(pnl_series: pd.Series, initial_cap: float) -> pd.Series:
    """
    Retorna a curva de capital acumulado:
    equity[t] = capital inicial + soma dos PnLs até t
    """
    return initial_cap + pnl_series.cumsum()


# ----------------------------------------------------
# DRAWDOWN
# ----------------------------------------------------
def compute_drawdown(equity: pd.Series) -> pd.DataFrame:
    """
    Calcula drawdown passo-a-passo.
    Retorna DataFrame com:
    - equity
    - roll_max
    - drawdown (proporção negativa)
    """
    roll_max = equity.cummax()
    dd = equity / roll_max - 1.0
    return pd.DataFrame({
        "equity": equity,
        "roll_max": roll_max,
        "drawdown": dd
    })


# ----------------------------------------------------
# PERFORMANCE SUMMARY
# ----------------------------------------------------
def performance_summary(trades: pd.DataFrame, initial_cap: float) -> dict:
    """
    Retorna métricas essenciais:
    - lucro líquido
    - win rate
    - profit factor
    - drawdown máximo
    - saldo final
    """
    if trades.empty:
        return {
            "initial_capital": initial_cap,
            "final_balance": initial_cap,
            "net_profit": 0.0,
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate_pct": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "profit_factor": 0.0,
            "max_drawdown_pct": 0.0,
        }

    final_balance = initial_cap + trades["pnl"].sum()

    wins = (trades["pnl"] > 0).sum()
    losses = (trades["pnl"] <= 0).sum()

    gross_profit = trades.loc[trades["pnl"] > 0, "pnl"].sum()
    gross_loss = trades.loc[trades["pnl"] <= 0, "pnl"].sum()

    win_rate = 100.0 * wins / len(trades)

    profit_factor = (
        gross_profit / abs(gross_loss) if gross_loss < 0 else np.inf
    )

    # Curva de equity e drawdown
    eq = equity_curve(trades["pnl"], initial_cap)
    dd_df = compute_drawdown(eq)
    max_dd = dd_df["drawdown"].min() * 100.0

    return {
        "initial_capital": round(initial_cap, 2),
        "final_balance": round(final_balance, 2),
        "net_profit": round(final_balance - initial_cap, 2),
        "trades": int(len(trades)),
        "wins": int(wins),
        "losses": int(losses),
        "win_rate_pct": round(win_rate, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "profit_factor": (
            round(profit_factor, 2) if np.isfinite(profit_factor) else np.inf
        ),
        "max_drawdown_pct": round(max_dd, 2),
    }
