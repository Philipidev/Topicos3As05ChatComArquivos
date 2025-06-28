"""
Arquivo de configuração centralizada para o assistente conversacional.
"""
import os
from dotenv import load_dotenv

if os.getenv("STREAMLIT_CLOUD") != "1":
    from dotenv import load_dotenv
    load_dotenv()


class Config:
    """Classe de configuração centralizada."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
    OPENAI_CHAT_MODEL = "gpt-4o"
    
    # Pinecone Configuration
    PINECONE_API_KEY = os.getenv('PINE_CONE_API_KEY')
    PINECONE_ENVIRONMENT = os.getenv('PINE_CONE_ENVIRONMENT', 'us-east-1-aws')
    PINECONE_INDEX_NAME = os.getenv('PINE_CONE_INDEX_NAME', 'pdf-assistant')
    
    # Application Configuration
    PDF_DIRECTORY = os.getenv('PDF_DIRECTORY', 'pdfs')
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
    
    # Search Configuration
    DEFAULT_TOP_K = int(os.getenv('DEFAULT_TOP_K', '5'))
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))
    
    @classmethod
    def validate_config(cls):
        """Valida se todas as configurações necessárias estão presentes."""
        required_vars = [
            ('OPENAI_API_KEY', cls.OPENAI_API_KEY),
            ('PINE_CONE_API_KEY', cls.PINECONE_API_KEY),
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(f"Variáveis de ambiente obrigatórias não encontradas: {', '.join(missing_vars)}")
        
        return True

