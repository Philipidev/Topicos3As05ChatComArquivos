"""
Módulo para extrair texto de arquivos PDF.
"""
import os
from typing import List, Dict
from pypdf import PdfReader


class PDFProcessor:
    """Classe responsável por processar arquivos PDF e extrair texto."""
    
    def __init__(self, pdf_directory: str = "pdfs"):
        """
        Inicializa o processador de PDF.
        
        Args:
            pdf_directory (str): Diretório onde estão os arquivos PDF.
        """
        self.pdf_directory = pdf_directory
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrai texto de um arquivo PDF específico.
        
        Args:
            pdf_path (str): Caminho para o arquivo PDF.
            
        Returns:
            str: Texto extraído do PDF.
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        
        except Exception as e:
            print(f"Erro ao processar PDF {pdf_path}: {str(e)}")
            return ""
    
    def process_all_pdfs(self) -> List[Dict[str, str]]:
        """
        Processa todos os PDFs no diretório especificado.
        
        Returns:
            List[Dict[str, str]]: Lista de dicionários com nome do arquivo e texto extraído.
        """
        documents = []
        
        if not os.path.exists(self.pdf_directory):
            print(f"Diretório {self.pdf_directory} não encontrado.")
            return documents
        
        pdf_files = [f for f in os.listdir(self.pdf_directory) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"Nenhum arquivo PDF encontrado no diretório {self.pdf_directory}.")
            return documents
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_directory, pdf_file)
            text = self.extract_text_from_pdf(pdf_path)
            
            if text:
                documents.append({
                    'filename': pdf_file,
                    'text': text,
                    'path': pdf_path
                })
                print(f"Processado: {pdf_file}")
            else:
                print(f"Falha ao processar: {pdf_file}")
        
        return documents
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Divide o texto em chunks menores para melhor processamento.
        
        Args:
            text (str): Texto a ser dividido.
            chunk_size (int): Tamanho máximo de cada chunk.
            overlap (int): Sobreposição entre chunks.
            
        Returns:
            List[str]: Lista de chunks de texto.
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Se não é o último chunk, tenta encontrar um ponto de quebra natural
            if end < len(text):
                # Procura por quebra de linha ou espaço próximo ao final
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in ['\n', '.', '!', '?', ' ']:
                        end = i + 1
                        break
            
            chunks.append(text[start:end].strip())
            start = end - overlap if end < len(text) else end
        
        return chunks

