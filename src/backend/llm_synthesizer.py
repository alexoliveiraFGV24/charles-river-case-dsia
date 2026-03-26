from  google import genai
from dotenv import load_dotenv
import os

load_dotenv()


def generate_ai_resume(ticker, text):
    # Instancia o cliente da nova SDK
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={
            "system_instruction": f"Aja como um sumarizador de dados purista do ticker {ticker}. Responda APENAS o resumo, sem preâmbulos."
        },
        contents=f"""
        REGRAS ESTRITAS:
        Use um ou dois parágrafos únicos, sem bullet points e sem fatos como fauramento, data de criação, lucro, entre outros.
        Mantenha o tom técnico e objetivo.
        Se o texto for inconsistente, priorize os dados factuais.

        TEXTO PARA RESUMIR:
        {text}"""
    )

    return response.text

def generate_ai_report(ticker, data):
    # Instancia o cliente da nova SDK
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={
            "system_instruction": f"Aja como um sumarizador de dados purista do ticker {ticker}. Responda APENAS o resumo, sem preâmbulos."
        },
        contents=f"""
        REGRAS ESTRITAS:
        Use um ou dois parágrafos únicos, sem bullet points e sem fatos como fauramento, data de criação, lucro, entre outros.
        Mantenha o tom técnico e objetivo.
        Se o texto for inconsistente, priorize os dados factuais.

        TEXTO PARA RESUMIR:
        {data}"""
    )

    return response.text
