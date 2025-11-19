# framework/strategies/ema_crossover.py
# ----------------------------------------------------
# Estratégia simples de cruzamento de EMAs:
# - Compra quando ema9 cruza acima da ema21
# - Venda quando ema9 cruza abaixo da ema21
# Retorna:
#   signals: DataFrame com datetime e coluna 'signal' (1, -1, 0)
#   indicadores_usados: lista de strings com nomes de colunas usadas
# ----------------------------------------------------

from typing import Tuple, List
import pandas as pd


def generate_signals(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Gera sinais de compra/venda baseado no cruzamento das EMAs 9 e 21.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame com pelo menos: 'datetime' e 'close'.
        Se não tiver 'ema9' e 'ema21', elas são calculadas.

    Retorno
    -------
    signals : pd.DataFrame
        Colunas:
            - datetime
            - signal: 1 (compra), -1 (venda), 0 (neutro)
    indicadores_usados : list[str]
        Lista com nomes dos indicadores utilizados.
    """
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])

    indicadores_usados = ["ema9", "ema21"]

    # Garante EMAs
    if "ema9" not in df.columns:
        df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()

    if "ema21" not in df.columns:
        df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()

    fast = df["ema9"]
    slow = df["ema21"]

    prev_fast = fast.shift(1)
    prev_slow = slow.shift(1)

    buy_signal = (prev_fast <= prev_slow) & (fast > slow)
    sell_signal = (prev_fast >= prev_slow) & (fast < slow)

    signals = pd.DataFrame({
        "datetime": df["datetime"],
        "signal": 0
    })

    signals.loc[buy_signal, "signal"] = 1
    signals.loc[sell_signal, "signal"] = -1

    return signals, indicadores_usados
