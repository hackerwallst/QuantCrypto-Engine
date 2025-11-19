# framework/indicators.py
# ----------------------------------------------------
# Pacote de indicadores técnicos estilo MT5.
# Cada função recebe df e retorna df com novas colunas.
# ----------------------------------------------------

import numpy as np
import pandas as pd


# ----------------------------------------------------
# Helpers
# ----------------------------------------------------
def _ensure_datetime_index(df):
    df = df.copy()
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])
    return df


# ----------------------------------------------------
# SMA – Simple Moving Average
# ----------------------------------------------------
def add_sma(df, period=20, col="close", name=None):
    df = df.copy()
    name = name or f"sma{period}"
    df[name] = df[col].rolling(period).mean()
    return df


# ----------------------------------------------------
# EMA – Exponential Moving Average
# ----------------------------------------------------
def add_ema(df, period=20, col="close", name=None):
    df = df.copy()
    name = name or f"ema{period}"
    df[name] = df[col].ewm(span=period, adjust=False).mean()
    return df


# ----------------------------------------------------
# RSI – Relative Strength Index
# ----------------------------------------------------
def add_rsi(df, period=14, col="close", name="rsi"):
    df = df.copy()
    delta = df[col].diff()

    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df[name] = 100 - (100 / (1 + rs))
    return df


# ----------------------------------------------------
# ATR – Average True Range
# ----------------------------------------------------
def add_atr(df, period=14, name="atr"):
    df = df.copy()
    high = df["high"]
    low = df["low"]
    close_prev = df["close"].shift(1)

    tr1 = high - low
    tr2 = (high - close_prev).abs()
    tr3 = (low - close_prev).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    df["tr"] = tr
    df[name] = tr.rolling(period).mean()
    return df


# ----------------------------------------------------
# ADX – Average Directional Index
# ----------------------------------------------------
def add_adx(df, period=14, name="adx"):
    df = df.copy()
    high = df["high"]
    low = df["low"]
    close_prev = df["close"].shift(1)

    tr1 = high - low
    tr2 = (high - close_prev).abs()
    tr3 = (low - close_prev).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    plus_dm = (high - high.shift(1)).where((high - high.shift(1)) > (low.shift(1) - low), 0.0)
    plus_dm = plus_dm.where(plus_dm > 0, 0.0)

    minus_dm = (low.shift(1) - low).where((low.shift(1) - low) > (high - high.shift(1)), 0.0)
    minus_dm = minus_dm.where(minus_dm > 0, 0.0)

    tr_n = tr.rolling(period).sum()
    plus_di = 100 * (plus_dm.rolling(period).sum() / tr_n.replace(0, np.nan))
    minus_di = 100 * (minus_dm.rolling(period).sum() / tr_n.replace(0, np.nan))

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)) * 100
    adx = dx.rolling(period).mean()

    df["plus_di"] = plus_di
    df["minus_di"] = minus_di
    df[name] = adx
    return df


# ----------------------------------------------------
# MACD – Moving Average Convergence Divergence
# ----------------------------------------------------
def add_macd(df, fast=12, slow=26, signal=9,
             col="close",
             name_macd="macd",
             name_signal="macd_signal",
             name_hist="macd_hist"):
    df = df.copy()

    ema_fast = df[col].ewm(span=fast, adjust=False).mean()
    ema_slow = df[col].ewm(span=slow, adjust=False).mean()

    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal

    df[name_macd] = macd
    df[name_signal] = macd_signal
    df[name_hist] = macd_hist
    return df


# ----------------------------------------------------
# Bollinger Bands
# ----------------------------------------------------
def add_bbands(df, period=20, std_mult=2,
               col="close",
               name_mid="bb_mid",
               name_up="bb_up",
               name_low="bb_low"):
    df = df.copy()

    ma = df[col].rolling(period).mean()
    std = df[col].rolling(period).std()

    df[name_mid] = ma
    df[name_up] = ma + std_mult * std
    df[name_low] = ma - std_mult * std
    return df


# ----------------------------------------------------
# Stochastic Oscillator
# ----------------------------------------------------
def add_stochastic(df, k_period=14, d_period=3,
                   name_k="stoch_k",
                   name_d="stoch_d"):
    df = df.copy()

    low_min = df["low"].rolling(k_period).min()
    high_max = df["high"].rolling(k_period).max()

    stoch_k = 100 * (df["close"] - low_min) / (high_max - low_min).replace(0, np.nan)
    stoch_d = stoch_k.rolling(d_period).mean()

    df[name_k] = stoch_k
    df[name_d] = stoch_d
    return df


# ----------------------------------------------------
# VWAP – Volume Weighted Average Price
# ----------------------------------------------------
def add_vwap(df, name="vwap"):
    df = df.copy()

    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    cum_tp_vol = (typical_price * df["volume"]).cumsum()
    cum_vol = df["volume"].cumsum().replace(0, np.nan)

    df[name] = cum_tp_vol / cum_vol
    return df


# ----------------------------------------------------
# SuperTrend (simplificado)
# ----------------------------------------------------
def add_supertrend(df, period=10, multiplier=3, name="supertrend"):
    df = add_atr(df, period=period)
    df = df.copy()

    hl2 = (df["high"] + df["low"]) / 2
    basic_ub = hl2 + multiplier * df["atr"]
    basic_lb = hl2 - multiplier * df["atr"]

    final_ub = basic_ub.copy()
    final_lb = basic_lb.copy()

    for i in range(1, len(df)):
        if (final_ub.iloc[i] > final_ub.iloc[i - 1]) or (df["close"].iloc[i - 1] > final_ub.iloc[i]):
            final_ub.iloc[i] = final_ub.iloc[i - 1]
        if (final_lb.iloc[i] < final_lb.iloc[i - 1]) or (df["close"].iloc[i - 1] < final_lb.iloc[i]):
            final_lb.iloc[i] = final_lb.iloc[i - 1]

    supertrend = pd.Series(index=df.index, dtype=float)

    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = final_ub.iloc[i]
        else:
            if (supertrend.iloc[i - 1] == final_ub.iloc[i - 1]) and (df["close"].iloc[i] <= final_ub.iloc[i]):
                supertrend.iloc[i] = final_ub.iloc[i]
            elif (supertrend.iloc[i - 1] == final_ub.iloc[i - 1]) and (df["close"].iloc[i] > final_ub.iloc[i]):
                supertrend.iloc[i] = final_lb.iloc[i]
            elif (supertrend.iloc[i - 1] == final_lb.iloc[i - 1]) and (df["close"].iloc[i] >= final_lb.iloc[i]):
                supertrend.iloc[i] = final_lb.iloc[i]
            else:
                supertrend.iloc[i] = final_ub.iloc[i]

    df[name] = supertrend
    return df


# ----------------------------------------------------
# PACOTE BÁSICO DE INDICADORES
# ----------------------------------------------------
def add_basic_indicators(df):
    """
    Adiciona um conjunto padrão de indicadores:
    - ema9, ema21
    - rsi14
    - atr14
    - macd (12, 26, 9)
    - bollinger 20/2
    """
    df = _ensure_datetime_index(df)
    df = add_ema(df, 9, name="ema9")
    df = add_ema(df, 21, name="ema21")
    df = add_rsi(df, 14, name="rsi14")
    df = add_atr(df, 14, name="atr14")
    df = add_macd(df)
    df = add_bbands(df, 20, 2)
    return df
