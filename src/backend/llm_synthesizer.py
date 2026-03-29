from  google import genai
from dotenv import load_dotenv
import os
import json


load_dotenv()


def generate_ai_resume(ticker, text):

    # Instancia o cliente
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # System Instruction
    system_instruction = (
        f"Você é um motor de sumarização purista para análise de equity ({ticker}). "
        "Sua saída deve conter exclusivamente o resumo textual, sem saudações, "
        "sem metadados e sem formatação de lista."
    )

    # Prompt de Conteúdo
    user_content = f"""
    Sintetize o texto abaixo focando estritamente em eventos corporativos, dinâmicas de setor ou fatos relevantes para o ticker {ticker}.

    REGRAS CRÍTICAS DE NEGÓCIO:
    1. FORMATO: Máximo de 2 parágrafos de prosa contínua. Proibido o uso de '-' ou '*' ou qualquer tipo de lista.
    2. FILTRO DE RUÍDO: Ignore sistematicamente: datas de fundação, biografias de executivos, valores de faturamento passados, lucro histórico ou descrições genéricas da empresa.
    3. FOCO: Priorize o "porquê" da notícia (ex: mudança de estratégia, impacto regulatório, nova parceria) em vez do "quem".
    4. INTEGRIDADE: Se o texto for contraditório, use apenas os fatos concretos e omita opiniões de colunistas.
    5. LINGUAGEM: Use terminologia de mercado financeiro (ex: 'market share', 'bottom-line', 'guidance', 'capex') de forma concisa.

    TEXTO BRUTO PARA PROCESSAMENTO:
    {text}
    """

    # Configuração do agente
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={
            "system_instruction": system_instruction,
            "temperature": 0.1,
            "top_p": 0.95,
        },
        contents=user_content
    )

    return response.text


def generate_ai_news_report(ticker, link):

    # Instancia o cliente
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # System Instruction
    system_instruction = (
        f"Você é um Analista de Equity especializado em {ticker}. "
        "Sua tarefa é processar notícias brutas e retornar uma análise estruturada em JSON. "
        "Não inclua nenhuma explicação fora do objeto JSON."
    )

    # Prompt de Conteúdo
    user_content = f"""
    Analise o conteúdo sobre {ticker} e preencha o seguinte objeto JSON:
    
    ESQUEMA ESPERADO:
    {{
        "resumo": "Texto de 1 a 2 parágrafos técnicos e fluidos, sem bullet points.",
        "classificacao": "POSITIVO, NEUTRO ou NEGATIVO",
        "pontos_chave": ["Fato relevante 1", "Fato relevante 2", "Fato relevante 3"],
        "sentimento_score": "Valor de -1.0 (muito pessimista) a 1.0 (muito otimista)"
    }}

    CONTEÚDO PARA ANALISAR:
    {link}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config={
            "system_instruction": system_instruction,
            "temperature": 0.1,
            "response_mime_type": "application/json"
        },
        contents=user_content
    )

    # Converte a string JSON em um dicionário
    try:
        dados_processados = json.loads(response.text)
        return dados_processados
    except json.JSONDecodeError:
        return {"erro": "Falha ao processar resposta da IA", "raw": response.text}



def generate_ai_report(ticker, data):
    pass