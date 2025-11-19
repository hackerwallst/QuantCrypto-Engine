# ============================================================
# RUN EXAMPLE — Framework de Backtest PRO para Cripto
# ============================================================

import os
import pandas as pd

from Framework.data_loader import load_ohlcv_csv
from Framework.indicators import add_basic_indicators
from Framework.backtester import Backtester
from Framework.metrics import performance_summary
from Framework.trade_plots import plot_equity, plot_drawdown, plot_candles_minimal
from Framework.monte_carlo import advanced_analysis_dashboard
from Framework.html_report import generate_html_report_base64

# ====== STRATEGIES ======
from Sample_Strategies.ema_cross_example import generate_signals as ema_signals
from Sample_Strategies.larry_williams_example import generate_signals as lw_signals


# ============================================================
# CONFIGURAÇÃO GLOBAL
# ============================================================
CONFIG = {
    "initial_capital": 1000.0,
    "single_position_mode": True,
    "commission_perc": 0.0004,  # 0.04%
    "slippage": 0.0001,         # 0.01%
}


# ============================================================
# ESCOLHER A ESTRATÉGIA AQUI
# ============================================================
STRATEGY_NAME = "ema_cross"   # ← troque para: "larry_williams"

if STRATEGY_NAME == "ema_cross":
    strategy_fn = ema_signals
elif STRATEGY_NAME == "larry_williams":
    strategy_fn = lw_signals
else:
    raise ValueError("Estratégia inválida.")


# ============================================================
# 1) CARREGAR HISTÓRICO
# ============================================================
DATA_PATH = "data/BTCUSDT_5m.csv"  # coloque seu CSV aqui

print("🔍 Carregando dados...")
df = load_ohlcv_csv(DATA_PATH)
df = add_basic_indicators(df)
print("✔ Dados carregados:", len(df), "velas")


# ============================================================
# 2) GERAR SINAIS DA ESTRATÉGIA
# ============================================================
print(f"⚡ Gerando sinais com a estratégia: {STRATEGY_NAME}")
signals, used_indicators = strategy_fn(df)
print("✔ Sinais gerados:", signals["signal"].value_counts().to_dict())


# ============================================================
# 3) RODAR BACKTEST
# ============================================================
print("🏁 Rodando Backtest PRO...")
bt = Backtester(df, CONFIG)
trades = bt.run(signals)

if trades is None or trades.empty:
    print("❌ Nenhum trade gerado pela estratégia.")
    exit()

print("✔ Total de trades:", len(trades))


# ============================================================
# 4) EXIBIR MÉTRICAS
# ============================================================
print("\n===== PERFORMANCE =====")
metrics = performance_summary(trades, CONFIG["initial_capital"])
for k, v in metrics.items():
    print(f"{k}: {v}")


# ============================================================
# 5) GRÁFICOS PRINCIPAIS
# ============================================================
print("\n📈 Plotando gráficos...")

plot_candles_minimal(df, "Histórico + Volume")
plot_equity(trades, CONFIG["initial_capital"])
plot_drawdown(trades, CONFIG["initial_capital"])


# ============================================================
# 6) ANÁLISE AVANÇADA (MONTE CARLO, ROBUSTEZ, ETC.)
# ============================================================
print("\n🧠 Rodando análise avançada (Monte Carlo, Robustez, Kelly)...")
advanced_analysis_dashboard(df, trades, CONFIG, CONFIG["initial_capital"])


# ============================================================
# 7) RELATÓRIO HTML COMPLETO
# ============================================================
print("\n📄 Gerando relatório HTML final...")

os.makedirs("reports", exist_ok=True)

generate_html_report_base64(
    df=df,
    trades=trades,
    config=CONFIG,
    initial_capital=CONFIG["initial_capital"],
    output_path="reports/backtest_report.html"
)

print("\n🎉 FINALIZADO!")
print("📁 Relatório salvo em: reports/backtest_report.html")
print("🚀 Framework pronto para explorar estratégias!")
