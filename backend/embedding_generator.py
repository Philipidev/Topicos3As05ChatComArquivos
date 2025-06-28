"""
Módulo para gerar embeddings usando a API do OpenAI.
"""
import os
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


class EmbeddingGenerator:
    """Classe responsável por gerar embeddings usando OpenAI."""
    
    def __init__(self, api_key: str = None):
        """
        Inicializa o gerador de embeddings.
        
        Args:
            api_key (str): Chave da API OpenAI. Se não fornecida, usa variável de ambiente.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("API key do OpenAI não encontrada. Configure OPENAI_API_KEY.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "text-embedding-ada-002"
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um texto específico.
        
        Args:
            text (str): Texto para gerar embedding.
            
        Returns:
            List[float]: Vetor de embedding.
        """
        try:
            # Remove quebras de linha excessivas e espaços
            cleaned_text = text.replace('\n', ' ').strip()
            
            if not cleaned_text:
                raise ValueError("Texto vazio fornecido.")
            
            response = self.client.embeddings.create(
                input=cleaned_text,
                model=self.model
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            print(f"Erro ao gerar embedding: {str(e)}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos.
        
        Args:
            texts (List[str]): Lista de textos para gerar embeddings.
            
        Returns:
            List[List[float]]: Lista de vetores de embedding.
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            try:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)
                print(f"Embedding gerado para texto {i+1}/{len(texts)}")
            
            except Exception as e:
                print(f"Erro ao gerar embedding para texto {i+1}: {str(e)}")
                # Adiciona um embedding vazio em caso de erro
                embeddings.append([])
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        Retorna a dimensão dos embeddings do modelo usado.
        
        Returns:
            int: Dimensão do embedding (1536 para text-embedding-ada-002).
        """
        return 1536  # Dimensão padrão do text-embedding-ada-002

