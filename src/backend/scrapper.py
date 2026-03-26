from bs4 import BeautifulSoup
import requests
import time
from dotenv import load_dotenv

from llm_synthesizer import *

load_dotenv()


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# Dados cadastrais usando o site Status Invest, Investidor 10 e um resumo usando Gemini
def get_cadastro_data(ticker, max_tries, sleep):
    
    # URLs usadas
    url_status = f"https://statusinvest.com.br/acoes/{ticker.lower()}"
    url_investidor_10 = f"https://investidor10.com.br/acoes/asai3/{ticker.lower()}"

    # Verificações básicas de conexão
    for i in range(max_tries):
        print(f"Tentativa {i+1}")
        response1 = requests.get(url_status, headers=HEADERS)
        response2 = requests.get(url_investidor_10, headers=HEADERS)
        if response1.status_code != 200 or response2.status_code != 200:
            print("Não conseguimos acessar a Status Invest ou a B3. Verifique o nome do ticker ou a conexão")
            time.sleep(sleep)
            if i == max_tries - 1:
                raise ConnectionError("Não conseguimos conectar")
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
    if nome:
        data["Nome da empresa"] = nome.text.strip()

    # Setor e Segmento
    atuacao = soup_status.find("div", class_='top-info top-info-1 top-info-sm-2 top-info-md-n sm d-flex justify-between')
    atuacao = atuacao.find_all("strong", class_='value')
    setor_atuacao = atuacao[0]
    segmento_atuacao = atuacao[2]
    if setor_atuacao:
        data["Setor de atuação"] = setor_atuacao.text.strip()
    if setor_atuacao:
        data["Segmento de atuação"] = segmento_atuacao.text.strip()

    # Modelo de negócio
    resumo_negocio = investidor_10.find("div", id="about-company")
    resumo_negocio = resumo_negocio.find("div", class_="text-content")
    if resumo_negocio:
        resumo_negocio = resumo_negocio.text.strip()
        data["Resumo do negócio"] = generate_ai_resume(ticker, resumo_negocio) # Resumo com AI
    else:
        data["Resumo do negócio"] = "Descrição não fornecida ou não encontrada"
    
    return data



# Dados de cotação usando os sites Fundamentus
def get_cotacao_data(ticker, max_tries, sleep):

    url_fundamentus = f"https://www.fundamentus.com.br/detalhes.php?papel={ticker.upper()}"

    for i in range(max_tries):
        print(f"Tentativa {i+1}")
        response1 = requests.get(url_fundamentus, headers=HEADERS)
        if response1.status_code != 200:
            print("Não conseguimos acessar a Fundamentus. Verifique o nome do ticker ou a conexão")
            time.sleep(sleep)
            if i == max_tries - 1:
                return None
        else:
            print("Conexão garantida")
            break
    
    soup_fundamentus = BeautifulSoup(response1.text, "html.parser")

 

    data = {}
  
    return data


# Indicadores fundamentalistas usando Investidor 10
def get_fundamentalista_data(ticker, max_tries, sleep):
    # Dados
    data = {}

    p_por_l = 0
    roe = 0
    divida_liquida_por_ebitda = 0
    margem_liquida = 0
    dividend_yield = 0 

    return data





# Notícias com a B3 e Trading View
def get_noticias_data(ticker, max_tries, sleep):
    data = {}
    return data


def get_full_report(ticker, max_tries, sleep):
    data = {}

    cadastro_data = get_cadastro_data(ticker, max_tries, sleep)
    # cotacao_data = get_cotacao_data(ticker, max_tries, sleep)
    # fundamentalista_data = get_fundamentalista_data(ticker, max_tries, sleep)
    # noticia_data = get_noticias_data(ticker, max_tries, sleep)

    data["Dados de cadastro"] = cadastro_data
    # data["Dados de cotação"] = cotacao_data
    # data["Indicadores fundamentalistas"] = fundamentalista_data
    # data["Notícias"] = noticia_data

    return data


if __name__ == "__main__":
    print(get_full_report("recv3", 5, 0))