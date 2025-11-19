# framework/data_quality.py
# ----------------------------------------------------
# DataQualitySuite – Validador avançado de integridade
# dos candles, inspirado no Tick Data Suite.
#
# Uso:
#   from framework.data_quality import DataQualitySuite
#   v = DataQualitySuite(df, timeframe="1h")
#   v.run()
#   v.report()
#
# ----------------------------------------------------

import pandas as pd
import numpy as np


class DataQualitySuite:
    """
    Analisa a consistência dos dados OHLCV, detectando:
    - gaps de timestamp
    - duplicados
    - ordem incorreta
    - candles inválidos
    - anomalias de preço (spikes)
    - anomalias de volume

    Gera um score final de 0 a 100.
    """

    def __init__(self, df: pd.DataFrame, timeframe: str):
        self.df = df.copy()
        self.timeframe = timeframe.lower()

        self.issues = {
            "timestamp_gaps": [],
            "timestamp_duplicates": [],
            "timestamp_out_of_order": [],
            "invalid_candles": [],
            "price_anomalies": [],
            "volume_anomalies": [],
        }

    # ------------------------------------------------
    # 1. Delta esperado entre candles
    # ------------------------------------------------
    def _expected_delta(self):
        tf_map = {
            "1m": 1, "5m": 5, "15m": 15, "30m": 30,
            "1h": 60, "2h": 120, "4h": 240,
            "1d": 1440,
        }
        minutes = tf_map.get(self.timeframe, 60)
        return pd.Timedelta(minutes=minutes)

    # ------------------------------------------------
    # 2. Verificar integridade de timestamps
    # ------------------------------------------------
    def check_timestamps(self):
        df = self.df.sort_values("datetime").reset_index(drop=True)
        exp = self._expected_delta()

        for i in range(len(df) - 1):
            t1 = df.loc[i, "datetime"]
            t2 = df.loc[i + 1, "datetime"]
            delta = t2 - t1

            if delta > exp:
                self.issues["timestamp_gaps"].append((i, t1, t2, delta))

            if delta.total_seconds() < 0:
                self.issues["timestamp_out_of_order"].append((i, t1, t2))

        dups = df[df["datetime"].duplicated()]["datetime"].tolist()
        self.issues["timestamp_duplicates"] = dups

    # ------------------------------------------------
    # 3. Validação interna dos candles
    # ------------------------------------------------
    def check_candle_integrity(self):
        df = self.df

        for i, row in df.iterrows():
            o, h, l, c = float(row.open), float(row.high), float(row.low), float(row.close)

            if not (l <= o <= h and l <= c <= h):
                self.issues["invalid_candles"].append((i, row.datetime))

            if o <= 0 or h <= 0 or l <= 0 or c <= 0:
                self.issues["invalid_candles"].append((i, row.datetime))

            if h < l:
                self.issues["invalid_candles"].append((i, row.datetime))

    # ------------------------------------------------
    # 4. Anomalias de preço (spikes)
    # ------------------------------------------------
    def check_price_anomalies(self):
        df = self.df.sort_values("datetime").reset_index(drop=True)
        df["range_pct"] = (df["high"] - df["low"]) / df["open"].replace(0, np.nan)

        anomalies = df[df["range_pct"] > 0.20]
        for idx, row in anomalies.iterrows():
            self.issues["price_anomalies"].append(
                (idx, row.datetime, float(row.range_pct))
            )

    # ------------------------------------------------
    # 5. Anomalias de volume
    # ------------------------------------------------
    def check_volume(self):
        df = self.df

        # Volume zero em tempos maiores que 1m é estranho
        if self.timeframe != "1m":
            vol_zero = df[df["volume"] == 0]
            for idx, row in vol_zero.iterrows():
                self.issues["volume_anomalies"].append((idx, row_]()
