import argparse
from src.config import DB_DSN
from src.fx_db import get_engine, ensure_fx_tables
from src.fx_extract import latest, historical
from src.fx_bronze_loader import load_fx_bronze
from src.fx_silver_transform import fx_to_silver_from_bronze
from src.fx_gold_enrich import enrich_latest_date

def main():
    """
    Função principal (CLI) que gerencia a execução dos estágios do pipeline de ETL de câmbio (FX).
    Permite configurar via argumentos de linha de comando a moeda base, moedas alvo,
    datas históricas e quais camadas (bronze, silver, gold) devem ser executadas.
    """
    # Configura o leitor de argumentos da linha de comando (CLI)
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", help="String de conexão DSN (por padrão utiliza o DB_DSN definido no arquivo .env)")
    ap.add_argument("--base", default="USD", help="Moeda base de referência para a cotação (ex.: USD, EUR, BRL)")
    ap.add_argument("--symbols", nargs="*", default=["BRL","EUR","GBP"], help="Lista de moedas alvo desejadas")
    ap.add_argument("--historical", help="Data específica no formato YYYY-MM-DD para buscar taxas históricas")
    ap.add_argument("--run", nargs="+", default=["bronze","silver"],
                    help="Estágios do pipeline a serem executados (opções: bronze, silver, gold)")
    ap.add_argument("--limit_pairs", type=int, default=200, help="Número máximo de pares processados no estágio GOLD")
    args = ap.parse_args()

    # Define o DSN do banco de dados (prioriza CLI, depois .env, e por fim define o SQLite local como fallback seguro)
    dsn = args.db or DB_DSN or "sqlite:///data/demo.sqlite"
    
    # Inicializa o engine do SQLAlchemy e garante que as tabelas necessárias existam
    engine = get_engine(dsn)
    ensure_fx_tables(engine)

    # ---------------------------------------------------------
    # ESTÁGIO BRONZE: Extração e Carga do dado bruto da API
    # ---------------------------------------------------------
    if "bronze" in args.run:
        # Se uma data histórica foi informada, busca o histórico; caso contrário, busca a cotação mais recente
        payload = historical(args.historical, base=args.base, symbols=args.symbols) if args.historical \
                  else latest(base=args.base, symbols=args.symbols)
        # Salva o payload cru na tabela bronze
        load_fx_bronze(engine, payload)
        print("[FX] Bronze inserido com sucesso.")

    # ---------------------------------------------------------
    # ESTÁGIO SILVER: Transformação e Tabularização dos dados
    # ---------------------------------------------------------
    if "silver" in args.run:
        # Converte os dados crus da camada bronze em registros tabulares limpos na camada silver
        inserted = fx_to_silver_from_bronze(engine, limit=20)
        print(f"[FX] Silver: {inserted} pares inseridos ou atualizados.")

    # ---------------------------------------------------------
    # ESTÁGIO GOLD: Enriquecimento analítico com Inteligência Artificial
    # ---------------------------------------------------------
    if "gold" in args.run:
        # Processa os dados da camada silver, calcula variações e utiliza a IA para gerar insights
        enriched = enrich_latest_date(engine, limit_pairs=args.limit_pairs)
        print(f"[FX] Gold: {enriched} pares enriquecidos com IA.")

if __name__ == "__main__":
    main()