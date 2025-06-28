"""
Interface Streamlit para o Assistente Conversacional baseado em LLM.
"""
import streamlit as st
import os
import sys
from typing import Dict, Any

# Adiciona o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.assistant import ConversationalAssistant
from backend.config import Config


def init_session_state():
    """Inicializa o estado da sessão."""
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'system_status' not in st.session_state:
        st.session_state.system_status = None


def check_environment_variables():
    """Verifica se as variáveis de ambiente estão configuradas."""
    required_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'PINE_CONE_API_KEY': os.getenv('PINE_CONE_API_KEY'),
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        st.error(f"⚠️ Variáveis de ambiente não configuradas: {', '.join(missing_vars)}")
        st.info("Configure as variáveis de ambiente no arquivo .env antes de usar o assistente.")
        return False
    
    return True


def initialize_assistant():
    """Inicializa o assistente conversacional."""
    try:
        if st.session_state.assistant is None:
            with st.spinner("Inicializando assistente..."):
                st.session_state.assistant = ConversationalAssistant()
                st.session_state.system_status = st.session_state.assistant.get_system_status()
        return True
    except Exception as e:
        st.error(f"Erro ao inicializar assistente: {str(e)}")
        return False


def display_system_status():
    """Exibe o status do sistema."""
    if st.session_state.system_status:
        status = st.session_state.system_status
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if status.get('pinecone_connected', False):
                st.success("🟢 Pinecone Conectado")
                st.metric("Vetores Indexados", status.get('total_vectors', 0))
            else:
                st.error("🔴 Pinecone Desconectado")
        
        with col2:
            st.info(f"📁 Diretório PDF: {status.get('pdf_directory', 'N/A')}")
            st.info(f"🤖 Modelo Embedding: {status.get('embedding_model', 'N/A')}")
        
        with col3:
            st.info(f"💬 Modelo Chat: {status.get('chat_model', 'N/A')}")
            if 'index_fullness' in status:
                st.metric("Ocupação do Índice", f"{status['index_fullness']:.1%}")


def handle_pdf_upload():
    """Gerencia o upload e processamento de PDFs."""
    st.subheader("📄 Gerenciamento de Documentos")
    
    # Upload de arquivos
    uploaded_files = st.file_uploader(
        "Faça upload de arquivos PDF",
        type=['pdf'],
        accept_multiple_files=True,
        help="Selecione um ou mais arquivos PDF para indexar"
    )
    
    if uploaded_files:
        # Salva arquivos na pasta pdfs
        pdf_dir = Config.PDF_DIRECTORY
        os.makedirs(pdf_dir, exist_ok=True)
        
        saved_files = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join(pdf_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files.append(uploaded_file.name)
        
        st.success(f"✅ {len(saved_files)} arquivo(s) salvos: {', '.join(saved_files)}")
        
        # Botão para indexar documentos
        if st.button("🔄 Indexar Documentos", type="primary"):
            with st.spinner("Processando e indexando documentos..."):
                result = st.session_state.assistant.index_pdfs()
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.info(f"📊 Documentos processados: {result['documents_processed']}")
                    st.info(f"📊 Chunks criados: {result['chunks_created']}")
                    st.info(f"📊 Embeddings gerados: {result['embeddings_generated']}")
                    
                    # Atualiza status do sistema
                    st.session_state.system_status = st.session_state.assistant.get_system_status()
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")
    
    # Lista arquivos existentes
    pdf_dir = Config.PDF_DIRECTORY
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
        if pdf_files:
            st.write("📁 **Arquivos PDF existentes:**")
            for file in pdf_files:
                st.write(f"• {file}")
        else:
            st.info("Nenhum arquivo PDF encontrado no diretório.")


def handle_chat_interface():
    """Gerencia a interface de chat."""
    st.subheader("💬 Chat com o Assistente")
    
    # Verifica se há vetores indexados
    if st.session_state.system_status and st.session_state.system_status.get('total_vectors', 0) == 0:
        st.warning("⚠️ Nenhum documento foi indexado ainda. Faça upload e indexe documentos primeiro.")
        return
    
    # Exibe histórico do chat
    for i, (question, answer, sources) in enumerate(st.session_state.chat_history):
        with st.container():
            st.write(f"**👤 Você:** {question}")
            st.write(f"**🤖 Assistente:** {answer}")
            
            if sources:
                with st.expander("📚 Fontes consultadas"):
                    for source in sources:
                        st.write(f"• {source['filename']} (similaridade: {source['score']:.3f})")
            
            st.divider()
    
    # Botão para limpar chat (fora do formulário)
    if st.button("🗑️ Limpar Chat"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Container para o formulário de pergunta
    with st.form(key="question_form", clear_on_submit=True):
        question = st.text_input(
            "Faça sua pergunta:",
            placeholder="Digite sua pergunta sobre os documentos..."
        )
        
        ask_button = st.form_submit_button("🚀 Perguntar", type="primary", use_container_width=True)
    
    if ask_button and question:
        with st.spinner("Processando pergunta..."):
            result = st.session_state.assistant.ask_question(question)
            
            if result['success']:
                # Adiciona ao histórico
                st.session_state.chat_history.append((
                    question,
                    result['answer'],
                    result['sources']
                ))
                st.rerun()
            else:
                st.error(f"❌ {result['message']}")


def main():
    """Função principal da aplicação."""
    st.set_page_config(
        page_title="Assistente Conversacional PDF",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Assistente Conversacional baseado em LLM")
    st.markdown("---")
    
    # Inicializa estado da sessão
    init_session_state()
    
    # Verifica variáveis de ambiente
    if not check_environment_variables():
        st.stop()
    
    # Inicializa assistente
    if not initialize_assistant():
        st.stop()
    
    # Sidebar com status do sistema
    with st.sidebar:
        st.header("📊 Status do Sistema")
        display_system_status()
        
        st.markdown("---")
        
        if st.button("🔄 Atualizar Status"):
            st.session_state.system_status = st.session_state.assistant.get_system_status()
            st.rerun()
    
    # Tabs principais
    tab1, tab2 = st.tabs(["💬 Chat", "📄 Documentos"])
    
    with tab1:
        handle_chat_interface()
    
    with tab2:
        handle_pdf_upload()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Assistente Conversacional PDF** - Desenvolvido com Streamlit, OpenAI e Pinecone"
    )


if __name__ == "__main__":
    main()

