import json
from sqlalchemy import text
from sqlalchemy.engine import Engine

def fx_to_silver_from_bronze(engine: Engine, limit: int = 20) -> int:
    """
    Transforma os dados brutos (JSON) armazenados na camada Bronze 
    em dados relacionais limpos e tabulados, salvando-os na camada Silver.
    
    Parâmetros:
        engine (Engine): Instância de conexão do SQLAlchemy com o banco de dados.
        limit (int): Número máximo de registros da tabela bronze a serem processados por vez.
        
    Retorno:
        int: Total de pares de moedas processados e inseridos/atualizados na camada Silver.
    """
    rows = 0
    
    # Inicia uma transação segura com o banco de dados
    with engine.begin() as conn:
        # Busca os registros mais recentes da tabela fx_bronze ordenados pelo ID decrescente
        res = conn.execute(text("""
            SELECT id, ref_date, base, raw_json
            FROM fx_bronze
            ORDER BY id DESC
            LIMIT :limit
        """), {"limit": limit})
        
        # Itera sobre cada payload bruto encontrado na camada Bronze
        for r in res.fetchall():
            # Converte a string JSON bruta de volta para um dicionário Python
            data = json.loads(r.raw_json)
            
            # Extrai o dicionário de taxas de câmbio (ex: {"BRL": 5.21, "EUR": 0.91}), garantindo um dicionário vazio se não houver dados
            rates = data.get("rates") or {}
            
            # Itera sobre cada par de moeda (símbolo e respectiva taxa de câmbio)
            for symbol, rate in rates.items():
                # Executa a inserção na tabela fx_silver aplicando um UPSERT:
                # Se já existir um registro com a mesma data (ref_date), base e símbolo, 
                # a taxa é atualizada (DO UPDATE SET rate=excluded.rate) em vez de duplicar.
                conn.execute(text("""
                    INSERT INTO fx_silver (ref_date, base, symbol, rate)
                    VALUES (:ref_date, :base, :symbol, :rate)
                    ON CONFLICT(ref_date, base, symbol) DO UPDATE SET rate=excluded.rate
                """), {
                    "ref_date": r.ref_date,
                    "base": r.base,
                    "symbol": symbol,
                    "rate": float(rate),
                })
                rows += 1
                
    # Retorna o total de linhas tabuladas e gravadas na camada Silver
    return rows