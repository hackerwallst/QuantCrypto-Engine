# framework/config.py
# ----------------------------------------------------
# Configurações padrão do QuantCrypto Engine.
# Este arquivo define parâmetros globais que podem ser
# sobrescritos pelo usuário no notebook ou scripts externos.

CONFIG = {
    "fee_pct": 0.0004,             # 0.04% por operação (approx. 0.08% ida+volta)
    "slippage_pct": 0.0001,        # 0.01% de slippage por execução
    "initial_cap": 1000.0,         # capital inicial do backtest
    "risk_per_trade_pct": 1.0,     # % do capital arriscado por trade
    "allow_short": False,          # Spot = False. Futuros = True
    "max_positions": 1,            # máximo de posições simultâneas
    "price_col": "close",          # coluna usada como preço de execução
}
