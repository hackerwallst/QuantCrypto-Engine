#!/usr/bin/env bash
echo "🚀 Instalando dependências do BTC Backtest Framework..."

# Opcional: cria/usa venv
# python -m venv .venv
# source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate     # Windows (PowerShell/CMD)

python -m pip install --upgrade pip

python -m pip install \
  pandas \
  numpy \
  matplotlib \
  seaborn \
  requests

echo "✅ Dependências instaladas com sucesso!"
