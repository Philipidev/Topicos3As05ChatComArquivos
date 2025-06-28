"""
Módulo para gerenciar operações com Pinecone.
"""
import os
import uuid
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

if os.getenv("STREAMLIT_CLOUD") != "1":
    from dotenv import load_dotenv
    load_dotenv()


class PineconeManager:
    """Classe responsável por gerenciar operações com Pinecone."""
    
    def __init__(self, api_key: str = None, environment: str = None, index_name: str = None):
        """
        Inicializa o gerenciador do Pinecone.
        
        Args:
            api_key (str): Chave da API Pinecone.
            environment (str): Ambiente do Pinecone.
            index_name (str): Nome do índice.
        """
        self.api_key = api_key or os.getenv('PINE_CONE_API_KEY')
        self.environment = environment or os.getenv('PINE_CONE_ENVIRONMENT', 'us-east-1-aws')
        self.index_name = index_name or os.getenv('PINE_CONE_INDEX_NAME', 'pdf-assistant')
        
        if not self.api_key:
            raise ValueError("API key do Pinecone não encontrada. Configure PINE_CONE_API_KEY.")
        
        # Inicializa o cliente Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
        
        # Conecta ou cria o índice
        self._setup_index()
    
    def _setup_index(self):
        """Configura o índice do Pinecone."""
        try:
            # Verifica se o índice já existe
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                print(f"Criando índice {self.index_name}...")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,  # Dimensão do text-embedding-ada-002
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                print(f"Índice {self.index_name} criado com sucesso.")
            else:
                print(f"Índice {self.index_name} já existe.")
            
            # Conecta ao índice
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            print(f"Erro ao configurar índice: {str(e)}")
            raise
    
    def upsert_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Insere ou atualiza documentos no índice.
        
        Args:
            documents (List[Dict[str, Any]]): Lista de documentos com metadados.
            embeddings (List[List[float]]): Lista de embeddings correspondentes.
        """
        if len(documents) != len(embeddings):
            raise ValueError("Número de documentos deve ser igual ao número de embeddings.")
        
        vectors = []
        
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            if not embedding:  # Pula embeddings vazios
                continue
            
            vector_id = str(uuid.uuid4())
            
            metadata = {
                'filename': doc.get('filename', ''),
                'text': doc.get('text', '')[:1000],  # Limita texto nos metadados
                'chunk_index': i,
                'full_text': doc.get('text', '')  # Texto completo
            }
            
            vectors.append({
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            })
        
        if vectors:
            try:
                # Insere em lotes de 100 (limite do Pinecone)
                batch_size = 100
                for i in range(0, len(vectors), batch_size):
                    batch = vectors[i:i + batch_size]
                    self.index.upsert(vectors=batch)
                    print(f"Inseridos {len(batch)} vetores (lote {i//batch_size + 1})")
                
                print(f"Total de {len(vectors)} vetores inseridos com sucesso.")
            
            except Exception as e:
                print(f"Erro ao inserir vetores: {str(e)}")
                raise
    
    def query_similar_documents(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca documentos similares baseado no embedding da query.
        
        Args:
            query_embedding (List[float]): Embedding da pergunta.
            top_k (int): Número de resultados a retornar.
            
        Returns:
            List[Dict[str, Any]]: Lista de documentos similares com scores.
        """
        try:
            response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            results = []
            for match in response.matches:
                result = {
                    'id': match.id,
                    'score': match.score,
                    'filename': match.metadata.get('filename', ''),
                    'text': match.metadata.get('full_text', ''),
                    'chunk_index': match.metadata.get('chunk_index', 0)
                }
                results.append(result)
            
            return results
        
        except Exception as e:
            print(f"Erro ao buscar documentos similares: {str(e)}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do índice.
        
        Returns:
            Dict[str, Any]: Estatísticas do índice.
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {str(e)}")
            return {}
    
    def delete_all_vectors(self):
        """Remove todos os vetores do índice."""
        try:
            self.index.delete(delete_all=True)
            print("Todos os vetores foram removidos do índice.")
        except Exception as e:
            print(f"Erro ao remover vetores: {str(e)}")
            raise

