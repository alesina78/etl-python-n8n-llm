import os
from dotenv import load_dotenv

# Carrega para o ambiente do sistema as variáveis definidas no arquivo .env
# (como DB_DSN, OPENAI_API_KEY, entre outras)
load_dotenv()

# Define a String de Conexão (DSN - Data Source Name) com o banco de dados.
# Por padrão, ele utiliza o SQLite local apontando para o arquivo demo.sqlite 
# localizado na pasta data/, mas o valor pode ser sobrescrito via linha de comando (CLI).
DB_DSN = os.getenv("DB_DSN", "sqlite:///data/demo.sqlite")

# Armazena a chave de autenticação da OpenAI.
# Conforme indicado, ela é exigida exclusivamente durante o estágio 'GOLD' do ETL,
# que é a etapa responsável por enriquecer e classificar dados utilizando Inteligência Artificial.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")