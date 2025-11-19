# framework/data_loader.py
# ----------------------------------------------------
# Loader HTTP da Binance para candles mensais.
# Versão profissional sem input() e pronta para uso em scripts/notebooks.

import pandas as pd
import requests
import zipfile
import io
from datetime import datetime, timedelta


# ----------------------------------------------------
# 1. Normalização do timeframe
# ----------------------------------------------------
def normalize_tf(tf: str) -> str:
    tf = tf.strip().lower()
    fix = {
        "1h": "1h", "h1": "1h",
        "4h": "4h", "h4": "4h",
        "1d": "1d", "d1": "1d",
        "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
    }
    return fix.get(tf, tf)


# ----------------------------------------------------
# 2. Baixar 1 mês da Binance
# ----------------------------------------------------
def download_binance_month(symbol: str, timeframe: str, year: int, month: int):
    file_name = f"{symbol}-{timeframe}-{year}-{month:02d}.zip"
    url = (
        f"https://data.binance.vision/data/spot/monthly/klines/"
        f"{symbol}/{timeframe}/{file_name}"
    )

    r = requests.get(url)
    if r.status_code != 200:
        print(f"[x] Arquivo inexistente: {url}")
        return None

    print(f"[OK] Baixado: {url}")

    z = zipfile.ZipFile(io.BytesIO(r.content))
    csv_name = z.namelist()[0]
    df = pd.read_csv(z.open(csv_name), header=None)

    df.columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ]

    # Filtro anti bugs de timestamp
    df = df[(df["open_time"] > 0) & (df["open_time"] < 32503680000000)]

    df["datetime"] = pd.to_datetime(df["open_time"], unit="ms")

    return df[["datetime", "open", "high", "low", "close", "volume"]]


# ----------------------------------------------------
# 3. Validação dos candles (duplicados e gaps)
# ----------------------------------------------------
def validate_data(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    print("\n============================")
    print("🔍 VALIDANDO CONSISTÊNCIA...")
    print("============================")

    df = df.sort_values("datetime").reset_index(drop=True)

    tf_map = {
        "1m": 1, "5m": 5, "15m": 15, "30m": 30,
        "1h": 60, "4h": 240, "1d": 1440,
    }

    size = tf_map.get(timeframe.lower(), 60)
    expected = timedelta(minutes=size)

    df["next"] = df["datetime"].shift(-1)
    df["diff"] = df["next"] - df["datetime"]

    gaps = df[df["diff"] > expected]
    dups = df[df["datetime"].duplicated()]

    print(f"Total: {len(df)}")
    print(f"Gaps detectados: {len(gaps)}")
    print(f"Duplicados removidos: {len(dups)}")

    df = df.drop_duplicates(subset="datetime")
    df = df.drop(columns=["next", "diff"], errors="ignore")

    return df


# ----------------------------------------------------
# 4. Loader principal (sem input; com parâmetros)
# ----------------------------------------------------
def fetch_binance_http(
    symbol: str,
    timeframe: str,
    start: datetime,
    end: datetime = None
):
    """
    Baixa candles da Binance via HTTP entre duas datas.

    Parâmetros:
        symbol  : "BTCUSDT"
        timeframe : "1m", "15m", "1h", etc
        start  : datetime inicial
        end    : datetime final (padrão = hoje)

    Retorna:
        DataFrame limpo com datetime, open, high, low, close, volume
    """

    timeframe = normalize_tf(timeframe)
    end = end or datetime.utcnow()

    print(f"[INFO] Baixando {symbol} {timeframe} de {start.date()} até {end.date()}...\n")

    dfs = []
    year = start.year
    month = start.month

    while (year < end.year) or (year == end.year and month <= end.month):

        print(f"Baixando {year}-{month:02d}...")
        df_month = download_binance_month(symbol, timeframe, year, month)

        if df_month is not None:
            dfs.append(df_month)

        month += 1
        if month > 12:
            month = 1
            year += 1

        # Para não baixar o mês atual (incompleto)
        if year == end.year and month == end.month:
            break

    if not dfs:
        raise ValueError("Nenhum dado foi encontrado no período solicitado.")

    full = pd.concat(dfs).sort_values("datetime").reset_index(drop=True)
    print(f"[OK] Total bruto: {len(full)} candles")

    clean = validate_data(full, timeframe)
    print(f"[FINAL] Total limpo: {len(clean)} candles")

    return clean
