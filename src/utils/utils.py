import unicodedata
import re

def limpar_palavra(texto: str) -> str:
    texto = texto.strip()    
    texto = texto.split(' ')[0]    
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')    
    texto = re.sub(r'[^a-zA-Z0-9]', '', texto)
    
    return texto

def parse_numero(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))