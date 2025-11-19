# framework/trade_utils.py
# ------------------------------------------------------------
# Utilidades para inspeção e exportação de trades:
# - validar existência do DataFrame
# - obter lista completa
# - obter últimos trades
# - exportar para CSV com segurança
# ------------------------------------------------------------

import pandas as pd


# ------------------------------------------------------------
# Verifica se trades é válido
# ------------------------------------------------------------
def validate_trades(trades):
    """
    Retorna (status, mensagem)
    status = False → trades inválido
    status = True  → trades válido
    """
    if trades is None:
        return False, "'trades' é None."
    if not isinstance(trades, pd.DataFrame):
        return False, f"'trades' não é DataFrame. Tipo: {type(trades)}"
    if trades.empty:
        return False, "Nenhum trade encontrado."
    return True, "ok"


# ------------------------------------------------------------
# Retorna a lista completa de trades
# ------------------------------------------------------------
def get_all_trades(trades: pd.DataFrame) -> pd.DataFrame:
    ok, msg = validate_trades(trades)
    if not ok:
        print(f"⚠ {msg}")
        return pd.DataFrame()
    return trades.copy()


# ------------------------------------------------------------
# Retorna os últimos N trades
# ------------------------------------------------------------
def get_last_trades(trades: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    ok, msg = validate_trades(trades)
    if not ok:
        print(f"⚠ {msg}")
        return pd.DataFrame()
    return trades.tail(n).copy()


# ------------------------------------------------------------
# Exporta trades para CSV com total segurança
# ------------------------------------------------------------
def export_trades_csv(trades: pd.DataFrame, path: str) -> bool:
    """
    Retorna True se o arquivo foi salvo.
    """
    ok, msg = validate_trades(trades)
    if not ok:
        print(f"⚠ Não exportado: {msg}")
        return False

    try:
        trades.to_csv(path, index=False)
        print(f"📁 Arquivo salvo com sucesso em: {path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar CSV: {e}")
        return False
