from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

def get_engine(dsn: str) -> Engine:
    """
    Cria e retorna uma instância do Engine do SQLAlchemy para conexão com o banco de dados.
    
    Parâmetros:
        dsn (str): String de conexão (Data Source Name), ex: "sqlite:///data/demo.sqlite".
        
    Retorno:
        Engine: Objeto de conexão configurado do SQLAlchemy.
    """
    # Cria o engine habilitando o suporte a recursos futuros (future=True)
    return create_engine(dsn, future=True)

def ensure_fx_tables(engine: Engine):
    """
    Garante que todas as tabelas e índices necessários para o pipeline de ETL (Camadas Bronze, Silver e Gold)
    existam no banco de dados. Caso não existam, elas são criadas automaticamente.
    
    Parâmetros:
        engine (Engine): Instância de conexão do SQLAlchemy com o banco de dados.
    """
    with engine.begin() as conn:
        # ---------------------------------------------------------
        # CAMADA BRONZE (Armazena o JSON cru extraído diretamente da API)
        # ---------------------------------------------------------
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS fx_bronze (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_date TEXT NOT NULL,                  -- Data de referência das taxas
            base TEXT NOT NULL,                      -- Moeda base (ex: USD)
            raw_json TEXT NOT NULL,                  -- Payload completo em formato JSON bruto
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Data/Hora em que o dado foi coletado
        )
        """))

        # ---------------------------------------------------------
        # CAMADA SILVER (Dados limpos e estruturados de forma tabulada por par de moedas)
        # ---------------------------------------------------------
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS fx_silver (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_date TEXT NOT NULL,
            base TEXT NOT NULL,
            symbol TEXT NOT NULL,                    -- Moeda de destino/câmbio (ex: BRL, EUR)
            rate REAL NOT NULL,                      -- Taxa de câmbio convertida
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        
        # Cria um índice único para evitar registros duplicados na camada Silver para a mesma data/par
        conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_fx_silver_unique
        ON fx_silver(ref_date, base, symbol)
        """))

        # ---------------------------------------------------------
        # CAMADA GOLD (Dados enriquecidos com cálculos analíticos e insights gerados por IA)
        # ---------------------------------------------------------
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS fx_gold (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_date TEXT NOT NULL,
            base TEXT NOT NULL,
            symbol TEXT NOT NULL,
            rate REAL NOT NULL,
            prev_date TEXT,                          -- Data do registro anterior (para comparação)
            prev_rate REAL,                          -- Taxa do registro anterior
            pct_change REAL,                         -- Variação percentual (ex.: 0.0123 = +1.23%)
            short_text TEXT,                         -- Resumo curto gerado por Inteligência Artificial
            analysis TEXT,                           -- Explicação analítica detalhada em 1-2 frases (IA)
            ia_notes TEXT,                           -- Notas de controle ou eventuais erros da IA
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        
        # Cria um índice único para garantir que cada par de moedas tenha apenas uma análise consolidada por data na Gold
        conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_fx_gold_unique
        ON fx_gold(ref_date, base, symbol)
        """))