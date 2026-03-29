import anthropic
import yfinance as yf
import json
import requests
from weasyprint import HTML
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO
# ============================================================
client = anthropic.Anthropic(api_key="SUA_API_KEY_AQUI")

TICKER_BR = "PETR4"           # Ticker sem .SA (ex: PETR4, VALE3, ITUB4)
TICKER_YF  = TICKER_BR + ".SA"  # Formato Yahoo Finance


# ============================================================
# 1. COLETA DE DADOS VIA YFINANCE
# ============================================================
def coletar_dados(ticker_yf: str) -> dict:
    print(f"📡 Coletando dados de {ticker_yf}...")
    t = yf.Ticker(ticker_yf)
    info = t.info

    # Cotação histórica (últimos 6 meses)
    hist = t.history(period="6mo")
    preco_atual   = round(info.get("currentPrice") or info.get("regularMarketPrice", 0), 2)
    preco_min_6m  = round(hist["Close"].min(), 2) if not hist.empty else None
    preco_max_6m  = round(hist["Close"].max(), 2) if not hist.empty else None
    variacao_6m   = round(
        ((hist["Close"].iloc[-1] / hist["Close"].iloc[0]) - 1) * 100, 2
    ) if not hist.empty else None

    # Indicadores fundamentalistas
    def fmt(val, decimais=2):
        try:
            return round(float(val), decimais) if val not in (None, "N/A", float("inf")) else "N/D"
        except:
            return "N/D"

    pl            = fmt(info.get("trailingPE"))
    roe           = fmt((info.get("returnOnEquity") or 0) * 100)
    margem_liq    = fmt((info.get("profitMargins") or 0) * 100)
    div_yield     = fmt((info.get("dividendYield") or 0) * 100)
    ebitda        = info.get("ebitda")
    divida_liq    = info.get("totalDebt")
    div_ebitda    = fmt(divida_liq / ebitda) if ebitda and divida_liq else "N/D"
    market_cap    = info.get("marketCap")
    market_cap_bi = fmt(market_cap / 1e9) if market_cap else "N/D"

    # Notícias (Yahoo Finance)
    noticias_raw = t.news[:5] if t.news else []
    noticias = [
        {
            "titulo": n.get("content", {}).get("title", "Sem título"),
            "url":    n.get("content", {}).get("canonicalUrl", {}).get("url", "#"),
        }
        for n in noticias_raw
    ]

    return {
        "ticker":       TICKER_BR,
        "nome":         info.get("longName", "N/D"),
        "setor":        info.get("sector", "N/D"),
        "industria":    info.get("industry", "N/D"),
        "pais":         info.get("country", "N/D"),
        "descricao":    info.get("longBusinessSummary", "N/D"),
        "cotacao": {
            "preco_atual":  preco_atual,
            "moeda":        info.get("currency", "BRL"),
            "min_6m":       preco_min_6m,
            "max_6m":       preco_max_6m,
            "variacao_6m_pct": variacao_6m,
            "market_cap_bi_brl": market_cap_bi,
        },
        "indicadores": {
            "P/L":                pl,
            "ROE (%)":            roe,
            "Margem Líquida (%)": margem_liq,
            "Dividend Yield (%)": div_yield,
            "Dívida Líq/EBITDA":  div_ebitda,
        },
        "noticias": noticias,
    }


# ============================================================
# 2. GERAÇÃO DO RELATÓRIO COM CLAUDE
# ============================================================
def gerar_relatorio_html(dados: dict) -> str:
    print("🤖 Enviando dados para Claude gerar o relatório...")

    PROMPT = f"""
Você é um analista fundamentalista sênior de renda variável brasileiro.

Com base nos dados abaixo, gere um relatório de análise fundamentalista completo em HTML,
pronto para impressão em PDF. Seja técnico, objetivo e profissional.

DADOS DA EMPRESA:
{json.dumps(dados, ensure_ascii=False, indent=2)}

ESTRUTURA OBRIGATÓRIA DO RELATÓRIO (em ordem):

1. CABEÇALHO
   - Logo fictício da empresa (use as iniciais do ticker em um círculo azul escuro)
   - Nome da empresa, ticker, setor e segmento (classificação B3)
   - Data de geração do relatório

2. DADOS CADASTRAIS
   - Nome, setor, segmento, país
   - Descrição resumida do modelo de negócio (baseada na descrição fornecida, em 3-4 linhas)

3. DADOS DE MERCADO
   - Preço atual, variação 6 meses, mínima/máxima 6 meses, market cap
   - Tabela com os 5 indicadores fundamentalistas formatados

4. INTERPRETAÇÃO DOS INDICADORES
   - Para cada indicador (P/L, ROE, Margem Líquida, Dividend Yield, Dívida/EBITDA):
     explique O QUE O NÚMERO SUGERE sobre a empresa, se está acima/abaixo da média
     do setor e o que isso implica para o investidor. Use linguagem analítica.

5. SÍNTESE DAS NOTÍCIAS
   - Liste cada notícia com título e URL clicável
   - Classifique cada uma como 🟢 Positiva, 🔴 Negativa ou 🟡 Neutra
   - Escreva 1-2 linhas de análise para cada notícia
   - Síntese geral do sentimento de mercado

6. TRÊS PERGUNTAS DO ANALISTA
   - Três perguntas críticas e específicas (baseadas nos dados reais)
     que um analista deveria investigar antes de tomar decisão de investimento

7. RODAPÉ
   - Aviso legal: "Este relatório foi gerado com auxílio de IA e não constitui recomendação de investimento."
   - Data e hora de geração

REGRAS DE FORMATAÇÃO:
- Gere APENAS o HTML completo (<!DOCTYPE html> até </html>), sem texto antes ou depois
- CSS inline completo, sem dependências externas (sem Google Fonts, sem CDN)
- Paleta: azul escuro (#1a2e4a), azul médio (#2e5090), branco (#ffffff), cinza claro (#f4f6f9), verde (#27ae60), vermelho (#e74c3c), amarelo (#f39c12)
- Fonte: Arial, Helvetica, sans-serif
- Margens adequadas para impressão: @media print com margin de 1.5cm
- Cards com sombra sutil para KPIs
- Tabelas com cabeçalho em azul escuro e linhas alternadas
- Divisores horizontais entre seções
- Evite page-break dentro de seções importantes no @media print
"""

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=8096,
        messages=[{"role": "user", "content": PROMPT}]
    )

    html = msg.content[0].text.strip()

    # Limpa possíveis marcações de código
    if html.startswith("```"):
        html = html.split("\n", 1)[1]
    if html.endswith("```"):
        html = html.rsplit("```", 1)[0]

    print(f"✅ HTML gerado | Tokens: {msg.usage.input_tokens} in / {msg.usage.output_tokens} out")
    return html.strip()


# ============================================================
# 3. SALVAR PDF
# ============================================================
def salvar_pdf(html: str, nome_arquivo: str):
    print(f"🖨️  Gerando PDF: {nome_arquivo}...")
    HTML(string=html).write_pdf(nome_arquivo)
    print(f"✅ PDF salvo: {nome_arquivo}")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    dados      = coletar_dados(TICKER_YF)
    html       = gerar_relatorio_html(dados)
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M")
    nome_pdf   = f"relatorio_{TICKER_BR}_{timestamp}.pdf"
    salvar_pdf(html, nome_pdf)
    print(f"\n🎉 Relatório completo: {nome_pdf}")