"""
Script para executar o assistente conversacional.
"""
import os
import sys
import subprocess

# Adiciona o diretório raiz ao path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def main():
    """Executa a aplicação Streamlit."""
    frontend_path = os.path.join(project_root, 'frontend', 'app.py')
    
    # Comando para executar o Streamlit
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', frontend_path,
        '--server.address', '0.0.0.0',
        '--server.port', '8501',
        '--server.headless', 'true'
    ]
    
    print("🚀 Iniciando Assistente Conversacional...")
    print(f"📁 Diretório do projeto: {project_root}")
    print("🌐 Acesse: http://localhost:8501")
    print("---")
    
    try:
        subprocess.run(cmd, cwd=project_root)
    except KeyboardInterrupt:
        print("\n👋 Assistente encerrado pelo usuário.")
    except Exception as e:
        print(f"❌ Erro ao executar aplicação: {str(e)}")

if __name__ == "__main__":
    main()

