# framework/plotting.py
# ------------------------------------------------------------
# Funções de plotagem de candles e volume.
# ------------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_candles_minimal(df: pd.DataFrame,
                         title: str = "Candles + Volume",
                         figsize=(19.2, 10.8),
                         verbose: bool = True):
    """
    Gráfico minimalista com:
    - Candles em cima
    - Volume embaixo
    - Focado em performance
    """
    if verbose:
        print("🟩 Gerando gráfico minimalista com volume...")

    data = df.copy()
    data.index = pd.to_datetime(data["datetime"])

    opens = data["open"].values
    highs = data["high"].values
    lows = data["low"].values
    closes = data["close"].values
    vols = data["volume"].values

    x = np.arange(len(data))

    fig, (ax_price, ax_vol) = plt.subplots(
        2, 1,
        figsize=figsize,
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )

    # PREÇO (CANDLES)
    up = closes >= opens
    down = closes < opens

    # Pavios
    ax_price.vlines(x[up], lows[up], highs[up], color="green", linewidth=0.4)
    ax_price.vlines(x[down], lows[down], highs[down], color="red", linewidth=0.4)

    # Corpo dos candles
    ax_price.vlines(x[up], opens[up], closes[up], color="green", linewidth=1.0)
    ax_price.vlines(x[down], opens[down], closes[down], color="red", linewidth=1.0)

    ax_price.set_title(title, fontsize=14)
    ax_price.set_ylabel("Preço")
    ax_price.grid(False)

    # VOLUME
    ax_vol.bar(x, vols, width=1.0, color="gray")
    ax_vol.set_ylabel("Volume")
    ax_vol.grid(False)

    plt.tight_layout()
    plt.show()

    if verbose:
        print("✔ Gráfico pronto!\n")
