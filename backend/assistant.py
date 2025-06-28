"""
Módulo principal do assistente conversacional.
Integra todos os componentes: processamento de PDF, geração de embeddings,
indexação no Pinecone e geração de respostas.
"""
from typing import List, Dict, Any
from openai import OpenAI
from .pdf_processor import PDFProcessor
from .embedding_generator import EmbeddingGenerator
from .pinecone_manager import PineconeManager
from .config import Config


class ConversationalAssistant:
    """Classe principal do assistente conversacional."""
    
    def __init__(self):
        """Inicializa o assistente conversacional."""
        # Valida configurações
        Config.validate_config()
        
        # Inicializa componentes
        self.pdf_processor = PDFProcessor(Config.PDF_DIRECTORY)
        self.embedding_generator = EmbeddingGenerator(Config.OPENAI_API_KEY)
        self.pinecone_manager = PineconeManager(
            Config.PINECONE_API_KEY,
            Config.PINECONE_ENVIRONMENT,
            Config.PINECONE_INDEX_NAME
        )
        
        # Cliente OpenAI para geração de respostas
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def index_pdfs(self) -> Dict[str, Any]:
        """
        Processa todos os PDFs e indexa no Pinecone.
        
        Returns:
            Dict[str, Any]: Resultado da indexação.
        """
        print("Iniciando processamento de PDFs...")
        
        # Processa PDFs
        documents = self.pdf_processor.process_all_pdfs()
        
        if not documents:
            return {
                'success': False,
                'message': 'Nenhum documento encontrado para processar.',
                'documents_processed': 0
            }
        
        # Prepara chunks de texto
        all_chunks = []
        chunk_metadata = []
        
        for doc in documents:
            chunks = self.pdf_processor.chunk_text(
                doc['text'],
                Config.CHUNK_SIZE,
                Config.CHUNK_OVERLAP
            )
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                chunk_metadata.append({
                    'filename': doc['filename'],
                    'text': chunk,
                    'path': doc['path'],
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
        
        print(f"Total de {len(all_chunks)} chunks criados.")
        
        # Gera embeddings
        print("Gerando embeddings...")
        embeddings = self.embedding_generator.generate_embeddings_batch(all_chunks)
        
        # Indexa no Pinecone
        print("Indexando no Pinecone...")
        self.pinecone_manager.upsert_documents(chunk_metadata, embeddings)
        
        return {
            'success': True,
            'message': 'Documentos indexados com sucesso.',
            'documents_processed': len(documents),
            'chunks_created': len(all_chunks),
            'embeddings_generated': len([e for e in embeddings if e])
        }
    
    def ask_question(self, question: str, top_k: int = None) -> Dict[str, Any]:
        """
        Responde uma pergunta baseada nos documentos indexados.
        
        Args:
            question (str): Pergunta do usuário.
            top_k (int): Número de documentos similares a buscar.
            
        Returns:
            Dict[str, Any]: Resposta e metadados.
        """
        if not question.strip():
            return {
                'success': False,
                'message': 'Pergunta não pode estar vazia.',
                'answer': '',
                'sources': []
            }
        
        top_k = top_k or Config.DEFAULT_TOP_K
        
        try:
            # Gera embedding da pergunta
            print("Gerando embedding da pergunta...")
            question_embedding = self.embedding_generator.generate_embedding(question)
            
            # Busca documentos similares
            print("Buscando documentos similares...")
            similar_docs = self.pinecone_manager.query_similar_documents(
                question_embedding,
                top_k
            )
            
            if not similar_docs:
                return {
                    'success': True,
                    'message': 'Nenhum documento relevante encontrado.',
                    'answer': 'Desculpe, não encontrei informações relevantes para responder sua pergunta.',
                    'sources': []
                }
            
            # Filtra documentos por threshold de similaridade
            relevant_docs = [
                doc for doc in similar_docs 
                if doc['score'] >= Config.SIMILARITY_THRESHOLD
            ]
            
            if not relevant_docs:
                return {
                    'success': True,
                    'message': 'Documentos encontrados não são suficientemente relevantes.',
                    'answer': 'Encontrei alguns documentos, mas eles não parecem ser muito relevantes para sua pergunta. Pode reformular a pergunta?',
                    'sources': []
                }
            
            # Prepara contexto para o GPT
            context = self._prepare_context(relevant_docs)
            
            # Gera resposta usando GPT
            print("Gerando resposta...")
            answer = self._generate_answer(question, context)
            
            # Prepara informações das fontes
            sources = [
                {
                    'filename': doc['filename'],
                    'score': round(doc['score'], 3),
                    'chunk_index': doc['chunk_index']
                }
                for doc in relevant_docs
            ]
            
            return {
                'success': True,
                'message': 'Resposta gerada com sucesso.',
                'answer': answer,
                'sources': sources,
                'documents_found': len(similar_docs),
                'relevant_documents': len(relevant_docs)
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao processar pergunta: {str(e)}',
                'answer': '',
                'sources': []
            }
    
    def _prepare_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Prepara o contexto a partir dos documentos relevantes.
        
        Args:
            documents (List[Dict[str, Any]]): Documentos relevantes.
            
        Returns:
            str: Contexto formatado.
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"Documento {i} ({doc['filename']}):")
            context_parts.append(doc['text'])
            context_parts.append("")  # Linha em branco
        
        return "\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Gera resposta usando GPT baseada na pergunta e contexto.
        
        Args:
            question (str): Pergunta do usuário.
            context (str): Contexto dos documentos relevantes.
            
        Returns:
            str: Resposta gerada.
        """
        prompt = f"""Você é um assistente especializado em responder perguntas baseado em documentos fornecidos.

Contexto dos documentos:
{context}

Pergunta: {question}

Instruções:
1. Responda a pergunta baseando-se APENAS nas informações fornecidas no contexto.
2. Se a informação não estiver disponível no contexto, diga que não encontrou a informação.
3. Seja claro, objetivo e cite os documentos quando relevante.
4. Mantenha um tom profissional e útil.

Resposta:"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=Config.OPENAI_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em responder perguntas baseado em documentos."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Erro ao gerar resposta: {str(e)}")
            return "Desculpe, ocorreu um erro ao gerar a resposta. Tente novamente."
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Retorna o status do sistema.
        
        Returns:
            Dict[str, Any]: Status dos componentes.
        """
        try:
            pinecone_stats = self.pinecone_manager.get_index_stats()
            
            return {
                'pinecone_connected': True,
                'total_vectors': pinecone_stats.get('total_vectors', 0),
                'index_dimension': pinecone_stats.get('dimension', 0),
                'index_fullness': pinecone_stats.get('index_fullness', 0),
                'pdf_directory': Config.PDF_DIRECTORY,
                'embedding_model': Config.OPENAI_EMBEDDING_MODEL,
                'chat_model': Config.OPENAI_CHAT_MODEL
            }
        
        except Exception as e:
            return {
                'pinecone_connected': False,
                'error': str(e),
                'pdf_directory': Config.PDF_DIRECTORY,
                'embedding_model': Config.OPENAI_EMBEDDING_MODEL,
                'chat_model': Config.OPENAI_CHAT_MODEL
            }

