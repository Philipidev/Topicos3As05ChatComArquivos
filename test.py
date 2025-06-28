"""
Script para testar os componentes do assistente conversacional.
"""
import os
import sys

# Adiciona o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Testa se todos os módulos podem ser importados."""
    print("🧪 Testando importações...")
    
    try:
        from backend.config import Config
        print("✅ Config importado com sucesso")
        
        from backend.pdf_processor import PDFProcessor
        print("✅ PDFProcessor importado com sucesso")
        
        from backend.embedding_generator import EmbeddingGenerator
        print("✅ EmbeddingGenerator importado com sucesso")
        
        from backend.pinecone_manager import PineconeManager
        print("✅ PineconeManager importado com sucesso")
        
        from backend.assistant import ConversationalAssistant
        print("✅ ConversationalAssistant importado com sucesso")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False


def test_environment():
    """Testa se as variáveis de ambiente estão configuradas."""
    print("\n🔧 Testando variáveis de ambiente...")
    
    required_vars = [
        'OPENAI_API_KEY',
        'PINE_CONE_API_KEY',
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Configurada")
        else:
            print(f"❌ {var}: Não configurada")
            missing_vars.append(var)
    
    optional_vars = [
        ('PINE_CONE_ENVIRONMENT', 'us-east-1-aws'),
        ('PINE_CONE_INDEX_NAME', 'pdf-assistant'),
        ('PDF_DIRECTORY', 'pdfs'),
    ]
    
    for var, default in optional_vars:
        value = os.getenv(var, default)
        print(f"ℹ️ {var}: {value}")
    
    return len(missing_vars) == 0, missing_vars


def test_pdf_directory():
    """Testa se o diretório de PDFs existe."""
    print("\n📁 Testando diretório de PDFs...")
    
    pdf_dir = os.getenv('PDF_DIRECTORY', 'pdfs')
    
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
        print(f"✅ Diretório {pdf_dir} existe")
        print(f"📄 Arquivos PDF encontrados: {len(pdf_files)}")
        
        if pdf_files:
            for file in pdf_files[:5]:  # Mostra até 5 arquivos
                print(f"   • {file}")
            if len(pdf_files) > 5:
                print(f"   ... e mais {len(pdf_files) - 5} arquivo(s)")
        else:
            print("ℹ️ Nenhum arquivo PDF encontrado")
        
        return True
    else:
        print(f"❌ Diretório {pdf_dir} não existe")
        return False


def test_basic_functionality():
    """Testa funcionalidades básicas sem conectar a APIs externas."""
    print("\n⚙️ Testando funcionalidades básicas...")
    
    try:
        from backend.pdf_processor import PDFProcessor
        
        # Testa inicialização do PDFProcessor
        processor = PDFProcessor()
        print("✅ PDFProcessor inicializado")
        
        # Testa chunking de texto
        test_text = "Este é um texto de teste. " * 100
        chunks = processor.chunk_text(test_text, chunk_size=200, overlap=50)
        print(f"✅ Chunking de texto: {len(chunks)} chunks criados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste básico: {str(e)}")
        return False


def main():
    """Executa todos os testes."""
    print("🧪 Iniciando testes do Assistente Conversacional")
    print("=" * 50)
    
    # Testa importações
    imports_ok = test_imports()
    
    # Testa variáveis de ambiente
    env_ok, missing_vars = test_environment()
    
    # Testa diretório de PDFs
    pdf_dir_ok = test_pdf_directory()
    
    # Testa funcionalidades básicas
    basic_ok = test_basic_functionality()
    
    # Resumo dos testes
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    print(f"Importações: {'✅ OK' if imports_ok else '❌ FALHA'}")
    print(f"Variáveis de ambiente: {'✅ OK' if env_ok else '❌ FALHA'}")
    print(f"Diretório de PDFs: {'✅ OK' if pdf_dir_ok else '❌ FALHA'}")
    print(f"Funcionalidades básicas: {'✅ OK' if basic_ok else '❌ FALHA'}")
    
    if not env_ok:
        print(f"\n⚠️ Variáveis não configuradas: {', '.join(missing_vars)}")
        print("Configure essas variáveis no arquivo .env antes de usar o assistente.")
    
    all_ok = imports_ok and env_ok and pdf_dir_ok and basic_ok
    
    if all_ok:
        print("\n🎉 Todos os testes passaram! O assistente está pronto para uso.")
        print("Execute 'python run.py' para iniciar a aplicação.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique as configurações antes de continuar.")
    
    return all_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

