from datetime import date

from src.database import *
from src.backend.scrapper import get_full_data


def _ativo_existe(session: Session, ticker: str) -> bool:
    return session.get(Ativo, ticker) is not None


def inserir_dados(session: Session, ticker: str, dados: dict, escala_clima: float | None = None) -> None:
    hoje = date.today()
    c    = dados["cadastral"]
    q    = dados["cotacao"]
    i    = dados["indicadores"]

    # ── Ativos (upsert simples: só insere se ainda não existir) ──────────────
    if not _ativo_existe(session, ticker.upper()):
        session.add(Ativo(
            Ticker                 = c["ticker"],
            EmpresaAtivo           = c["empresa"],
            SetorAtuacaoEmpresa    = c["setor"],
            SegmentoAtuacaoEmpresa = c["segmento"],
            ResumoEmpresa          = c["resumo"],
        ))
        session.flush()   # garante FK antes das próximas inserções

    # ── DadosCotacao ─────────────────────────────────────────────────────────
    session.add(DadosCotacao(
        DataConsulta        = hoje,
        Ticker              = c["ticker"],
        Cotacao             = q["cotacao"],
        DataUltimaCotacao   = q["data_ultima_cotacao"],
        Min52semanas        = q["min_52"],
        Max52semanas        = q["max_52"],
        VolumeMedio2Meses   = q["volume_medio_2m"],
        ValorMercado        = q["valor_mercado"],
        NumeroAcoes         = q["num_acoes"],
        DataUltimoBalanco   = q["data_ultimo_balanco"],
    ))

    # ── IndicadoresFundamentalistas ──────────────────────────────────────────
    session.add(IndicadoresFundamentalistas(
        DataConsulta        = hoje,
        Ticker              = c["ticker"],
        PL                  = i["pl"],
        ROE                 = i["roe"],
        DividaLiquidaEBITDA = i["div_liq_ebitda"],
        MargemLiquida       = i["margem_liquida"],
        DividendYield       = i["dividend_yield"],
    ))

    # ── Clima ────────────────────────────────────────────────────────────────
    session.add(Clima(
        DataConsulta = hoje,
        Ticker       = c["ticker"],
        Escala       = escala_clima,
    ))


# ══════════════════════════════════════════════════════════════════════════════
#  EXECUÇÃO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Cria as tabelas caso ainda não existam
    Base.metadata.create_all(engine)
    print("Tabelas verificadas/criadas.\n")

    tickers = ["PETR4.SA", "VALE3.SA"]

    with Session(engine) as session:
        for ticker in tickers:
            print(f"Coletando {ticker}...")
            try:
                dados = get_full_data(ticker)
                inserir_dados(
                    session,
                    ticker,
                    dados,
                    escala_clima=None,   # preencha com o valor desejado
                )
                print(f"{ticker} inserido.")
            except Exception as e:
                print(f"Erro em {ticker}: {e}")

        session.commit()
        print("\nCommit realizado")


# Exemplo
# if __name__ == "__main__":
#     main()