# framework/backtester.py
# ------------------------------------------------------------
# Backtester PRO Universal
# ------------------------------------------------------------
# Recursos:
# - single_position_mode (1 trade por vez) ou hedge (múltiplos trades)
# - SL / TP opcionais
# - trailing stop opcional
# - sinais simples (signal)
# - sinais ricos (stop_price, size, risk, trailing_distance)
# ------------------------------------------------------------

import pandas as pd
import numpy as np


class Backtester:
    """
    Backtester PRO universal para o QuantCrypto Engine.
    
    Funcionalidades:
        - Suporta modo single-position (1 trade por vez) ou hedge (múltiplos trades)
        - Suporta SL, TP e Trailing Stop opcionais
        - Suporta sinais simples (apenas 'signal') ou enriquecidos
        - Calcula MAE, MFE, Risk:Reward, duração, etc.
    """

    def __init__(self, df: pd.DataFrame, config: dict = None):
        self.df = df.copy().reset_index(drop=True)
        self.df["datetime"] = pd.to_datetime(self.df["datetime"])

        self.config = config or {}
        self.initial_capital = float(self.config.get("initial_capital", 1000.0))
        self.single_position_mode = bool(self.config.get("single_position_mode", True))
        self.commission_perc = float(self.config.get("commission_perc", 0.0))  # % do nocional
        self.slippage = float(self.config.get("slippage", 0.0))                # fração do preço

    # ------------------------------------------------------------
    # FUNÇÃO PRINCIPAL
    # ------------------------------------------------------------
    def run(self, signals: pd.DataFrame) -> pd.DataFrame:
        if signals is None or signals.empty:
            return pd.DataFrame()

        sig = signals.copy()
        sig["datetime"] = pd.to_datetime(sig["datetime"])

        # join por datetime
        data = pd.merge(
            self.df,
            sig,
            on="datetime",
            how="left",
        )

        # se não tiver coluna signal, assume 0
        if "signal" not in data.columns:
            data["signal"] = 0
        data["signal"] = data["signal"].fillna(0).astype(int)

        has_stop  = "stop_price" in data.columns
        has_take  = "take_price" in data.columns
        has_size  = "size" in data.columns
        has_risk  = "risk" in data.columns
        has_trail = "trailing_distance" in data.columns

        open_trades = []
        closed_trades = []
        trade_id = 0

        # --------------------------------------------------------
        # LOOP CANDLE A CANDLE
        # --------------------------------------------------------
        for bar_index, row in enumerate(data.itertuples()):
            dt = row.datetime
            o, h, l, c = row.open, row.high, row.low, row.close
            sigv = row.signal

            # =====================================================
            # 1) Atualizar trades abertos (SL/TP/Trailing)
            # =====================================================
            still_open = []
            for t in open_trades:
                direction = t["direction"]
                size = t["size"]
                entry_px = t["entry_price"]

                # --- MFE / MAE ---
                if direction == "long":
                    best_pnl = (h - entry_px) * size
                    worst_pnl = (l - entry_px) * size
                else:  # short
                    best_pnl = (entry_px - l) * size
                    worst_pnl = (entry_px - h) * size

                t["max_favor"] = max(t["max_favor"], best_pnl)
                t["max_adverse"] = min(t["max_adverse"], worst_pnl)

                exit_reason = None
                exit_price = None

                # --- Trailing Stop (opcional) ---
                if t.get("trailing_distance") is not None:
                    dist = t["trailing_distance"]
                    if direction == "long":
                        new_stop = c - dist
                        if t["stop_price"] is None or np.isnan(t["stop_price"]):
                            t["stop_price"] = new_stop
                        else:
                            t["stop_price"] = max(t["stop_price"], new_stop)
                    else:
                        new_stop = c + dist
                        if t["stop_price"] is None or np.isnan(t["stop_price"]):
                            t["stop_price"] = new_stop
                        else:
                            t["stop_price"] = min(t["stop_price"], new_stop)

                # --- Checagem SL / TP ---
                sp = t.get("stop_price", None)
                tp = t.get("take_price", None)

                hit_sl = False
                hit_tp = False

                if direction == "long":
                    if sp is not None and not pd.isna(sp) and l <= sp:
                        hit_sl = True
                    if tp is not None and not pd.isna(tp) and h >= tp:
                        hit_tp = True
                else:
                    if sp is not None and not pd.isna(sp) and h >= sp:
                        hit_sl = True
                    if tp is not None and not pd.isna(tp) and l <= tp:
                        hit_tp = True

                if hit_sl or hit_tp:
                    if hit_sl:
                        exit_price = sp
                        exit_reason = "sl"
                    else:
                        exit_price = tp
                        exit_reason = "tp"

                # --- Fechamento por SL/TP ---
                if exit_reason is not None:
                    self._close_trade(
                        t, exit_price, dt, bar_index, exit_reason=exit_reason
                    )
                    closed_trades.append(t)
                else:
                    still_open.append(t)

            open_trades = still_open

            # =====================================================
            # 2) FECHAMENTO POR SINAL (single_position_mode)
            # =====================================================
            if self.single_position_mode and sigv != 0 and len(open_trades) > 0:
                for t in open_trades:
                    self._close_trade(
                        t, c, dt, bar_index, exit_reason="signal"
                    )
                    closed_trades.append(t)
                open_trades = []

                # abre nova posição seguindo o sinal
                new_trade = self._open_trade_from_row(
                    trade_id, dt, c, row, bar_index,
                    has_stop, has_take, has_size, has_risk, has_trail
                )
                if new_trade is not None:
                    open_trades.append(new_trade)
                    trade_id += 1

            # =====================================================
            # 3) ABERTURA DE TRADES (modo hedge OU sem posição)
            # =====================================================
            else:
                if sigv != 0:
                    if self.single_position_mode and len(open_trades) > 0:
                        # já tratado acima
                        pass
                    else:
                        new_trade = self._open_trade_from_row(
                            trade_id, dt, c, row, bar_index,
                            has_stop, has_take, has_size, has_risk, has_trail
                        )
                        if new_trade is not None:
                            open_trades.append(new_trade)
                            trade_id += 1

        # =========================================================
        # 4) Fecha o que sobrou no último candle (EOD)
        # =========================================================
        if len(open_trades) > 0:
            last_row = data.iloc[-1]
            last_dt = last_row["datetime"]
            last_c = last_row["close"]
            last_idx = len(data) - 1
            for t in open_trades:
                self._close_trade(
                    t, last_c, last_dt, last_idx, exit_reason="eod"
                )
                closed_trades.append(t)

        if not closed_trades:
            return pd.DataFrame()

        trades_df = pd.DataFrame(closed_trades)

        # Duração e barras em trade
        trades_df["duration"] = trades_df["exit_time"] - trades_df["entry_time"]
        trades_df["bars_in_trade"] = (
            trades_df["exit_bar_index"] - trades_df["entry_bar_index"]
        )

        # resultado textual
        trades_df["result"] = np.where(
            trades_df["pnl"] > 0, "win",
            np.where(trades_df["pnl"] < 0, "loss", "be")
        )

        # Risk safe
        if "risk" not in trades_df.columns:
            trades_df["risk"] = np.nan
        trades_df["risk"] = trades_df["risk"].astype(float)

        trades_df["risk_reward"] = np.where(
            trades_df["risk"].notna() & (trades_df["risk"] != 0),
            trades_df["pnl"] / trades_df["risk"],
            np.nan
        )

        return trades_df

    # ------------------------------------------------------------
    # ABERTURA DE TRADE POR LINHA DE SINAL
    # ------------------------------------------------------------
    def _open_trade_from_row(
        self, trade_id, dt, price, sig_row, bar_index,
        has_stop, has_take, has_size, has_risk, has_trail
    ):
        sigv = sig_row.signal
        if sigv == 0:
            return None

        direction = "long" if sigv > 0 else "short"
        size = float(getattr(sig_row, "size", 1.0)) if has_size else 1.0

        stop_price = getattr(sig_row, "stop_price", None) if has_stop else None
        take_price = getattr(sig_row, "take_price", None) if has_take else None
        trailing_distance = getattr(sig_row, "trailing_distance", None) if has_trail else None
        risk = getattr(sig_row, "risk", None) if has_risk else None

        # limpa None/nan
        if stop_price is not None and pd.isna(stop_price):
            stop_price = None
        if take_price is not None and pd.isna(take_price):
            take_price = None
        if trailing_distance is not None and pd.isna(trailing_distance):
            trailing_distance = None
        if risk is not None and pd.isna(risk):
            risk = None

        # se a estratégia não definiu risk, tenta inferir pelo SL
        if risk is None and stop_price is not None:
            risk = abs(price - stop_price) * size

        dir_factor = 1 if direction == "long" else -1
        entry_px = price * (1 + dir_factor * self.slippage)
        commission_open = self.commission_perc * entry_px * size

        trade = {
            "id": trade_id,
            "direction": direction,
            "entry_time": dt,
            "entry_bar_index": bar_index,
            "entry_price": entry_px,
            "size": size,
            "stop_price": stop_price,
            "take_price": take_price,
            "trailing_distance": trailing_distance,
            "risk": risk,
            "max_favor": 0.0,
            "max_adverse": 0.0,
            "volume_at_entry": getattr(sig_row, "volume", None),
            "exit_time": None,
            "exit_bar_index": None,
            "exit_price": None,
            "pnl": None,
            "commission_open": commission_open,
            "commission_close": 0.0,
            "exit_reason": None,
        }
        return trade

    # ------------------------------------------------------------
    # FECHAMENTO DE TRADE (PnL, COMISSÃO, SLIPPAGE...)
    # ------------------------------------------------------------
    def _close_trade(self, trade, exit_price, exit_time, exit_bar_index, exit_reason="unknown"):
        direction = trade["direction"]
        size = trade["size"]
        dir_factor = 1 if direction == "long" else -1

        # aplica slippage na saída
        px = exit_price * (1 - dir_factor * self.slippage)

        commission_close = self.commission_perc * px * size

        gross_pnl = (px - trade["entry_price"]) * size * dir_factor
        net_pnl = gross_pnl - trade.get("commission_open", 0.0) - commission_close

        trade["exit_time"] = exit_time
        trade["exit_bar_index"] = exit_bar_index
        trade["exit_price"] = px
        trade["commission_close"] = commission_close
        trade["pnl"] = net_pnl
        trade["exit_reason"] = exit_reason
