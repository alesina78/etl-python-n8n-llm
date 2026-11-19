import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente definidas no arquivo .env local
load_dotenv()

# --- Configurações do Banco de Dados ---
# Define a String de Conexão (DSN) para o SQLite local na pasta data/
DB_DSN = os.getenv("DB_DSN", "sqlite:///data/demo.sqlite")

# --- Configurações de Inteligência Artificial (Ollama / Local) ---
# O Ollama local não exige chave real, mas mantemos um valor padrão ("ollama")
# para satisfazer a validação exigida pelo SDK cliente da OpenAI.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")

# Define o modelo local padrão que foi baixado no seu Ollama (ex: llama3)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "llama3")

# Aponta para a API compatível com OpenAI rodando localmente na sua máquina
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")