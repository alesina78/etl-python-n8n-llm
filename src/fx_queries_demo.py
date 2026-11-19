import argparse
import pandas as pd
from sqlalchemy import text
from src.fx_db import get_engine

def main():
    """
    Função principal (CLI) para consulta e exibição rápida no terminal 
    dos registros mais recentes armazenados nas tabelas fx_silver e fx_gold.
    Utiliza o Pandas para formatar os resultados em formato de tabela legível.
    """
    # Configura os argumentos aceitos via linha de comando
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", help="String de conexão DSN (opcional)")
    args = ap.parse_args()

    # Obtém o engine blindado (aceita DSN opcional da CLI ou usa o SQLite padrão)
    engine = get_engine(args.db)

    # Abre uma conexão ativa com o banco para realizar as consultas de inspeção
    with engine.connect() as conn:
        # ---------------------------------------------------------
        # CONSULTA 1: Exibe os últimos registros da Camada Silver
        # ---------------------------------------------------------
        print("\n== fx_silver (últimos 12 registros) ==")
        q1 = text("""
            SELECT ref_date, base, symbol, rate
            FROM fx_silver
            ORDER BY ref_date DESC, symbol
            LIMIT 12
        """)
        # Carrega o resultado da query diretamente em um DataFrame do Pandas e imprime formatado
        print(pd.read_sql(q1, conn))

        # ---------------------------------------------------------
        # CONSULTA 2: Exibe os últimos registros enriquecidos da Camada Gold
        # ---------------------------------------------------------
        print("\n== fx_gold (últimos 12 registros) ==")
        q2 = text("""
            SELECT ref_date, base, symbol, rate, prev_date, prev_rate,
                   ROUND(pct_change*100,2) AS pct_change_pct, -- Converte a taxa decimal em percentual formatado
                   short_text, analysis, ia_notes
            FROM fx_gold
            ORDER BY ref_date DESC, symbol
            LIMIT 12
        """)
        # Exibe as análises e resumos gerados pela Inteligência Artificial
        print(pd.read_sql(q2, conn))

if __name__ == "__main__":
    main()