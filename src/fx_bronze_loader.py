import json
from sqlalchemy import text
from sqlalchemy.engine import Engine

def load_fx_bronze(engine: Engine, payload: dict) -> int:
    """
    Carrega o payload bruto (dados crus) de taxas de câmbio na tabela Bronze do banco de dados.
    
    Exemplo de payload esperado da API Frankfurter:
    {"amount": 1.0, "base": "USD", "date": "2025-08-26", "rates": {"EUR": 0.91, "BRL": 5.21}}
    
    Parâmetros:
        engine (Engine): Instância de conexão do SQLAlchemy com o banco de dados.
        payload (dict): Dicionário contendo os dados brutos obtidos da API.
        
    Retorno:
        int: Retorna 1 indicando que a inserção foi executada com sucesso.
    """
    
    # Extrai a data de referência das cotações a partir do dicionário do payload
    ref_date = payload.get("date")
    
    # Extrai a moeda base das cotações a partir do dicionário do payload
    base = payload.get("base")
    
    # Inicia uma transação segura com o banco de dados utilizando o SQLAlchemy
    with engine.begin() as conn:
        # Executa o comando SQL de inserção na tabela fx_bronze
        # O payload completo é transformado em uma string JSON para armazenamento raw (bruto)
        conn.execute(text("""
            INSERT INTO fx_bronze (ref_date, base, raw_json)
            VALUES (:ref_date, :base, :raw_json)
        """), {
            "ref_date": ref_date, 
            "base": base, 
            "raw_json": json.dumps(payload, ensure_ascii=False)
        })
        
    # Retorna o status de sucesso da operação de carga
    return 1