import json
import math
from typing import Optional, Tuple
from sqlalchemy import text
from sqlalchemy.engine import Engine
from openai import OpenAI
from src.config import OPENAI_API_KEY

# Prompt de Sistema (System Prompt) que define o comportamento, 
# papel e regras restritivas para o modelo de Inteligência Artificial.
SYS = """Você é um analista financeiro.
Dado um par cambial (base→symbol), a taxa atual, a taxa anterior e a variação percentual,
gere um texto curto e uma explicação em PT-BR, claros e objetivos.

REGRAS:
- Responda APENAS um objeto JSON (sem markdown, sem ```).
- Chaves: short_text, analysis, ia_notes.
- short_text: até ~80 caracteres (ex.: "USD→BRL 5,21 (+0,8% vs ontem)").
- analysis: 1–2 frases simples, sem jargão excessivo.
- ia_notes: deixe vazio se tudo ok.
- Use vírgula como separador decimal (pt-BR).
"""

def _fmt_pct(p: Optional[float]) -> str:
    """Formata um valor percentual para o padrão brasileiro (ex: 0.0123 -> '1,23%')."""
    if p is None or math.isnan(p):
        return "0,0%"
    return f"{p*100:.2f}%".replace(".", ",")

def _fmt_rate(r: Optional[float]) -> str:
    """Formata a taxa de câmbio para exibir com vírgula e 4 casas decimais."""
    if r is None or math.isnan(r):
        return "-"
    return f"{r:.4f}".replace(".", ",")

def _call_llm(client: OpenAI, base: str, symbol: str, ref_date: str,
              rate: float, prev_date: Optional[str], prev_rate: Optional[float],
              pct_change: Optional[float]) -> dict:
    """
    Envia os dados do par de moedas para a API da OpenAI (GPT-4o-mini) 
    e retorna um dicionário estruturado com o resumo e a análise de tendência.
    """
    # Prepara o payload de dados que o modelo irá analisar
    user = {
        "pair": f"{base}->{symbol}",
        "ref_date": ref_date,
        "rate": rate,
        "prev_date": prev_date,
        "prev_rate": prev_rate,
        "pct_change": pct_change
    }
    
    # Chamada à API de Chat Completions da OpenAI
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYS},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)}
        ],
        temperature=0.0,  # Temperatura zero garante respostas determinísticas e precisas
    )
    
    raw = resp.choices[0].message.content
    
    # Tenta converter a resposta da IA de string JSON para dicionário Python
    try:
        data = json.loads(raw)
    except Exception:
        # Fallback de segurança caso a IA retorne um formato inválido
        trend = "estável"
        if pct_change is not None:
            if pct_change > 0.0005:
                trend = "alta"
            elif pct_change < -0.0005:
                trend = "queda"
        data = {
            "short_text": f"{base}→{symbol} { _fmt_rate(rate) } ({trend})",
            "analysis": "Resumo gerado sem JSON estruturado pelo modelo.",
            "ia_notes": f"parse_error: {raw[:180]}"
        }
        
    # Garante que todas as chaves obrigatórias estejam presentes no dicionário
    for k in ("short_text", "analysis", "ia_notes"):
        data.setdefault(k, "")
    return data

def _prev_point(engine: Engine, base: str, symbol: str, ref_date: str) -> Tuple[Optional[str], Optional[float]]:
    """Busca a amostra imediatamente anterior a ref_date para um determinado par (base, symbol) na camada Silver."""
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT ref_date, rate
            FROM fx_silver
            WHERE base=:base AND symbol=:symbol AND ref_date < :ref_date
            ORDER BY ref_date DESC
            LIMIT 1
        """), {"base": base, "symbol": symbol, "ref_date": ref_date}).first()
        if row:
            return row.ref_date, float(row.rate)
        return None, None

def enrich_latest_date(engine: Engine, limit_pairs: int = 200) -> int:
    """
    Orquestra a Camada Gold: encontra a data mais recente no fx_silver, 
    calcula a variação em relação ao dia anterior, consulta a IA para gerar 
    insights e salva/atualiza (UPSERT) os resultados consolidados na tabela fx_gold.
    """
    # Valida se a chave da OpenAI foi configurada no ambiente
    if not OPENAI_API_KEY:
        raise RuntimeError("Defina OPENAI_API_KEY no .env para rodar o GOLD de FX.")
    client = OpenAI(api_key=OPENAI_API_KEY)

    with engine.begin() as conn:
        # Identifica a data mais recente armazenada na camada Silver
        latest = conn.execute(text("""
            SELECT ref_date FROM fx_silver
            ORDER BY ref_date DESC
            LIMIT 1
        """)).scalar()
        if not latest:
            return 0

        # Busca os pares de moedas correspondentes à data mais recente
        pairs = conn.execute(text("""
            SELECT base, symbol, rate
            FROM fx_silver
            WHERE ref_date = :d
            ORDER BY base, symbol
            LIMIT :lim
        """), {"d": latest, "lim": limit_pairs}).fetchall()

        inserted = 0
        for p in pairs:
            base, symbol, rate = p.base, p.symbol, float(p.rate)
            
            # Obtém a cotação e a data anterior para o cálculo de variação
            prev_date, prev_rate = _prev_point(engine, base, symbol, latest)

            pct_change = None
            if prev_rate and prev_rate != 0:
                pct_change = (rate - prev_rate) / prev_rate

            # Chama o serviço de IA para obter a análise textual do par
            gen = _call_llm(client, base, symbol, latest, rate, prev_date, prev_rate, pct_change)

            # Insere os dados enriquecidos na tabela fx_gold (com UPSERT para evitar duplicatas)
            conn.execute(text("""
                INSERT INTO fx_gold
                (ref_date, base, symbol, rate, prev_date, prev_rate, pct_change,
                 short_text, analysis, ia_notes)
                VALUES
                (:ref_date, :base, :symbol, :rate, :prev_date, :prev_rate, :pct_change,
                 :short_text, :analysis, :ia_notes)
                ON CONFLICT(ref_date, base, symbol) DO UPDATE SET
                  rate=excluded.rate,
                  prev_date=excluded.prev_date,
                  prev_rate=excluded.prev_rate,
                  pct_change=excluded.pct_change,
                  short_text=excluded.short_text,
                  analysis=excluded.analysis,
                  ia_notes=excluded.ia_notes
            """), {
                "ref_date": latest,
                "base": base,
                "symbol": symbol,
                "rate": rate,
                "prev_date": prev_date,
                "prev_rate": prev_rate,
                "pct_change": pct_change,
                "short_text": gen["short_text"],
                "analysis": gen["analysis"],
                "ia_notes": gen["ia_notes"]
            })
            inserted += 1

    return inserted