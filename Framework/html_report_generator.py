from report_html import generate_html_report_base64
# ou, se estiver em pacote:
# from framework.report_html import generate_html_report_base64

generate_html_report_base64(
    df,
    trades,
    CONFIG,
    initial_capital=CONFIG.get("initial_cap", 1000.0),
    output_path="backtest_report.html",  # ou /content/... se estiver no Colab
)
