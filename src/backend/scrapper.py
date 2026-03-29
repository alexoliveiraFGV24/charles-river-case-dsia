from bs4 import BeautifulSoup
import requests
import time
from dotenv import load_dotenv
import numpy as np

from src.utils import *
from src.backend.llm_synthesizer import *


load_dotenv()


# Dados cadastrais usando o site Status Invest, Investidor 10 e um resumo usando Gemini
def get_cadastro_data(ticker, max_tries, sleep):
    
    # URLs usadas
    url_status = f"https://statusinvest.com.br/acoes/{ticker.lower()}"
    url_investidor_10 = f"https://investidor10.com.br/acoes/{ticker.lower()}"

    # Verificações básicas de conexão
    for i in range(max_tries):
        print(f"Tentativa {i+1}")
        response1 = requests.get(url_status)
        response2 = requests.get(url_investidor_10)
        if response1.status_code != 200 or response2.status_code != 200:
            print(f"Não conseguimos acessar a Status Invest ou a Investidor 10. Verifique o nome do ticker ou a conexão. Status: {response1.status_code} e {response2.status_code}")
            time.sleep(sleep)
            if i == max_tries - 1:
                return None
        else:
            print("Conexão garantida")
            break
    
    # Criando instâncias para webscrapping
    soup_status = BeautifulSoup(response1.text, "html.parser")
    investidor_10 = BeautifulSoup(response2.text, "html.parser")

    # Dados
    data = {}

    # Nome da empresa
    nome = soup_status.find("span", class_='d-block fw-600 text-main-green-dark')        

    # Setor e Segmento
    atuacao = soup_status.find("div", class_='top-info top-info-1 top-info-sm-2 top-info-md-n sm d-flex justify-between')
    atuacao = atuacao.find_all("strong", class_='value')
    setor_atuacao = atuacao[0]
    segmento_atuacao = atuacao[2]

    # Modelo de negócio
    resumo_negocio = investidor_10.find("div", id="about-company")
    resumo_negocio = resumo_negocio.find("div", class_="text-content")

    # Frase de não encontrado
    nao_encontrado = "Não encontrado(a)"

    # Preenchendo os dados
    if nome:
        data["Nome empresa"] = nome.text.strip()
    else:
        data["Nome empresa"] = nao_encontrado

    if setor_atuacao:
        data["Setor de atuação"] = setor_atuacao.text.strip()
    else:
        data["Setor de atuação"] = nao_encontrado

    if segmento_atuacao:
        data["Segmento de atuação"] = segmento_atuacao.text.strip()
    else:
        data["Segmento de atuação"] = nao_encontrado

    if resumo_negocio:
        resumo_negocio = resumo_negocio.text.strip()
        data["Resumo do negócio (IA)"] = generate_ai_resume(ticker, resumo_negocio) # Resumo com AI
    else:
        data["Resumo do negócio (IA)"] = nao_encontrado

    # Retornando
    return data



# Dados de cotação usando os sites Fundamentus
def get_cotacao_data(ticker, max_tries, sleep):

    # URL usada
    url_fundamentus = f"https://www.fundamentus.com.br/detalhes.php?papel={ticker.upper()}"

    # Verificações bássicas de conexão
    for i in range(max_tries):
        print(f"Tentativa {i+1}")
        response = requests.get(url_fundamentus)
        if response.status_code != 200:
            print(f"Não conseguimos acessar a Fundamentus. Verifique o nome do ticker ou a conexão. Status: {response.status_code}")
            time.sleep(sleep)
            if i == max_tries - 1:
                return None
        else:
            print("Conexão garantida")
            break
    
    # Criando a instância para o web scrapping
    soup_fundamentus = BeautifulSoup(response.text, "html.parser")

    # Dados
    data = {}

    # Fiz essa separação pois há duas tabelas com os dados de cotação no site Fundamentos
    dados_cotacao = soup_fundamentus.find_all("table", class_="w728")
    dados_cotacao1 = dados_cotacao[0].find_all("span", class_="txt")
    dados_cotacao2 = dados_cotacao[1].find_all("span", class_="txt")

    # Dados de cotação
    cotacao = dados_cotacao1[3].text.strip()
    data_ultima_cotacao = dados_cotacao1[7].text.strip()
    min_52_sem = dados_cotacao1[11].text.strip()
    max_52_sem = dados_cotacao1[15].text.strip()
    volume_medio_negociacao_2_meses = dados_cotacao1[19].text.strip()
    valor_mercado = dados_cotacao2[1].text.strip()
    ult_balanco_process = dados_cotacao2[3].text.strip()
    valor_firma = dados_cotacao2[5].text.strip()
    num_acoes = dados_cotacao2[7].text.strip()

    # Frase de não encontrado
    nao_encontrado = "Não encontrado(a)"

    # Preenchendo os dados
    if cotacao:
        data["Cotação"] = parse_numero(cotacao)
    else:
        data["Cotação"] = nao_encontrado

    if data_ultima_cotacao:
        data["Data última cotação"] = parse_data(data_ultima_cotacao)
    else:
        data["Data última cotação"] = nao_encontrado

    if min_52_sem:
        data["Mínimo 52 semanas"] = parse_numero(min_52_sem)
    else:
        data["Mínimo 52 semanas"] = nao_encontrado

    if max_52_sem:
        data["Máximo 52 semanas"] = parse_numero(max_52_sem)
    else:
        data["Máximo 52 semanas"] = nao_encontrado

    if volume_medio_negociacao_2_meses:
        data["Volume médio de negociação (2 meses)"] = parse_numero(volume_medio_negociacao_2_meses)
    else:
        data["Volume médio de negociação (2 meses)"] = nao_encontrado
    
    if valor_mercado:
        data["Valor de mercado"] = parse_numero(valor_mercado)
    else:
        data["Valor de mercado"] = nao_encontrado

    if valor_firma:
        data["valor da firma"] = parse_numero(valor_firma)
    else:
        data["valor da firma"] = nao_encontrado

    if ult_balanco_process:
        data["Último balanço processado"] = parse_data(ult_balanco_process)
    else:
        data["Último balanço processado"] = nao_encontrado

    if num_acoes:
        data["Número de ações"] = parse_numero(num_acoes)
    else:
        data["Número de ações"] = nao_encontrado
    
    # Retornando
    return data



# Indicadores fundamentalistas usando Investidor 10
def get_fundamentalista_data(ticker, max_tries, sleep):

    # URL usada
    url_investidor = f"https://investidor10.com.br/acoes/{ticker.lower()}/"

    # Verificações bássicas de conexão
    for i in range(max_tries):
        print(f"Tentativa {i+1}")
        response = requests.get(url_investidor)
        if response.status_code != 200:
            print(f"Não conseguimos acessar a Fundamentus. Verifique o nome do ticker ou a conexão. Status: {response.status_code}")
            time.sleep(sleep)
            if i == max_tries - 1:
                return None
        else:
            print("Conexão garantida")
            break
    
    # Criando a instância para o web scrapping
    soup_investidor = BeautifulSoup(response.text, "html.parser")
    indicadores_fundamentalistas = soup_investidor.find("div", id="table-indicators", class_="table table-bordered outter-borderless")
    indicadores_fundamentalistas = indicadores_fundamentalistas.find_all("div", class_="value d-flex justify-content-between align-items-center")

    # Dados
    data = {}

    # Indicadores fundamentalistas
    p_por_l = indicadores_fundamentalistas[0].text.strip()
    dividend_yield = indicadores_fundamentalistas[3].text.strip()
    margem_liquida = indicadores_fundamentalistas[5].text.strip()
    roe = indicadores_fundamentalistas[19].text.strip()
    divida_liquida_por_ebitda = indicadores_fundamentalistas[23].text.strip()

    # Frase de não encontrado
    nao_encontrado = "Não encontrado(a)"

    # Preenchendo os dados
    if p_por_l:
        data["P/L"] = parse_numero(p_por_l)
    else:
        data["P/L"] = nao_encontrado

    if roe:
        data["ROE (%)"] = parse_numero(roe)/100
    else:
        data["ROE (%)"] = nao_encontrado

    if divida_liquida_por_ebitda:
        data["Dívida Líquida/EBTIDA"] = parse_numero(divida_liquida_por_ebitda)
    else:
        data["Dívida Líquida/EBTIDA"] = nao_encontrado

    if margem_liquida:
        data["Margem Líquida (%)"] = parse_numero(margem_liquida)/100
    else:
        data["Margem Líquida (%)"] = nao_encontrado

    if dividend_yield:
        data["Dividend Yield (%)"] = parse_numero(dividend_yield)/100
    else:
        data["Dividend Yield (%)"] = nao_encontrado

    # Retornando
    return data



# Notícias com a API Trading View e resumo com IA
def get_noticias_data(ticker, max_tries, sleep):

    # URL usada
    url_trading = f"https://news-mediator.tradingview.com/public/view/v1/symbol?filter=lang%3Apt&filter=symbol%3ABMFBOVESPA%3A{ticker.upper()}&client=landing&streaming=false&user_prostatus=non_pr"

    # Verificações bássicas de conexão
    for i in range(max_tries):
        print(f"Tentativa {i+1}")
        response = requests.get(url_trading)
        if response.status_code != 200:
            print(f"Não conseguimos acessar a API de notícias do Trading View. Verifique o nome do ticker ou a conexão. Status: {response.status_code}")
            time.sleep(sleep)
            if i == max_tries - 1:
                return None
        else:
            print("Conexão garantida")
            break
    
    # Resposta do json
    todas_noticias = response.json()["items"]

    # Dados
    data = {}

    # Pegando 5 notícias
    noticias = np.random.choice(todas_noticias, size=5)

    # Fazendo um resumo e classificando cada uma delas
    for i in range(1):
        if noticias[i]["storyPath"]:
            url_noticia = "https://br.tradingview.com" + todas_noticias[i]["storyPath"]
            resumo, classificador = generate_ai_news_report(ticker, url_noticia)
            data[f"Notícia {i+1}"] = (url_noticia, resumo, classificador)
        else:
            data[f"Notícia {i+1}"] = "Não encontrado(a)"

    # Retornando
    return data


# Gerando todos os dados
def get_full_report(ticker, max_tries, sleep):
    data = {}

    cadastro_data = get_cadastro_data(ticker, max_tries, sleep)
    cotacao_data = get_cotacao_data(ticker, max_tries, sleep)
    fundamentalista_data = get_fundamentalista_data(ticker, max_tries, sleep)
    noticia_data = get_noticias_data(ticker, max_tries, sleep)

    data["Dados de cadastro"] = cadastro_data
    data["Dados de cotação"] = cotacao_data
    data["Indicadores fundamentalistas"] = fundamentalista_data
    data["Notícias"] = noticia_data

    return data


# Exemplo
# if __name__ == "__main__":
#     print(get_full_report("recv3", 5, 0))