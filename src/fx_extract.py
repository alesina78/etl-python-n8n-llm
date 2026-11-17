import requests
from typing import Dict, Any, List

# Define a URL base da API Frankfurter (uma API pública e gratuita de câmbio que não exige chave de API)
BASE_URL = "https://api.frankfurter.app"

def latest(base: str = "USD", symbols: List[str] | None = None) -> Dict[str, Any]:
    """
    Busca as taxas de câmbio mais recentes disponíveis na API Frankfurter.
    
    Parâmetros:
        base (str): Moeda base de referência (ex: "USD", "EUR"). Padrão é "USD".
        symbols (List[str] | None): Lista opcional de moedas de destino para filtrar a cotação (ex: ["BRL", "EUR"]).
        
    Retorno:
        Dict[str, Any]: Dicionário contendo o JSON de resposta da API com as taxas atuais.
    """
    # Prepara os parâmetros da requisição garantindo que a moeda base esteja em letras maiúsculas
    params = {"from": base.upper()}
    
    # Se foram especificadas moedas de destino, converte todas para maiúsculas e as une separadas por vírgula
    if symbols:
        params["to"] = ",".join([s.upper() for s in symbols])
        
    # Executa a requisição GET para o endpoint '/latest' com um timeout de segurança de 20 segundos
    r = requests.get(f"{BASE_URL}/latest", params=params, timeout=20)
    
    # Lança uma exceção automaticamente caso a requisição retorne algum código de erro HTTP (ex: 404, 500)
    r.raise_for_status()
    
    # Retorna os dados convertidos de JSON para um dicionário Python
    return r.json()

def historical(date: str, base: str = "USD", symbols: List[str] | None = None) -> Dict[str, Any]:
    """
    Busca as taxas de câmbio históricas para uma data específica na API Frankfurter.
    
    Parâmetros:
        date (str): Data de referência no formato YYYY-MM-DD (ex: "2025-08-26").
        base (str): Moeda base de referência (ex: "USD"). Padrão é "USD".
        symbols (List[str] | None): Lista opcional de moedas de destino para filtrar.
        
    Retorno:
        Dict[str, Any]: Dicionário contendo o JSON de resposta da API com as taxas daquela data.
    """
    # Prepara os parâmetros da requisição com a moeda base em maiúsculas
    params = {"from": base.upper()}
    
    # Adiciona as moedas de destino aos parâmetros caso tenham sido informadas
    if symbols:
        params["to"] = ",".join([s.upper() for s in symbols])
        
    # Executa a requisição GET direcionada para o endpoint dinâmico com a data desejada (ex: /2025-08-26)
    r = requests.get(f"{BASE_URL}/{date}", params=params, timeout=20)
    
    # Garante que a resposta foi bem-sucedida
    r.raise_for_status()
    
    # Retorna o payload decodificado em formato de dicionário Python
    return r.json()