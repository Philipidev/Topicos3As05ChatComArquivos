# Assistente Conversacional baseado em LLM

## Visão Geral

Este projeto implementa um assistente conversacional baseado em Large Language Models (LLM) capaz de indexar vetores (embeddings textuais) de uma coleção de documentos PDF e responder perguntas através de uma interface de conversação intuitiva.

O sistema utiliza tecnologias de ponta como OpenAI GPT-4 para geração de embeddings e respostas, Pinecone para indexação e busca vetorial, e Streamlit para a interface de usuário, criando uma solução completa e robusta para análise e consulta de documentos.

## Características Principais

### 🤖 Processamento Inteligente de Documentos
- Extração automática de texto de arquivos PDF
- Divisão inteligente de documentos em chunks para otimizar o processamento
- Geração de embeddings usando o modelo text-embedding-ada-002 da OpenAI
- Indexação vetorial eficiente no Pinecone para busca semântica

### 💬 Interface Conversacional Avançada
- Interface web intuitiva desenvolvida com Streamlit
- Chat interativo com histórico de conversas
- Upload de documentos via drag-and-drop
- Visualização em tempo real do status do sistema

### 🔍 Busca Semântica Inteligente
- Busca por similaridade semântica usando embeddings
- Filtragem por threshold de relevância
- Citação automática das fontes consultadas
- Respostas contextualizadas baseadas nos documentos indexados

### ⚙️ Arquitetura Modular e Escalável
- Separação clara entre backend e frontend
- Configuração centralizada via variáveis de ambiente
- Componentes independentes e testáveis
- Fácil manutenção e extensão

## Arquitetura do Sistema

### Componentes Backend

#### PDFProcessor (`backend/pdf_processor.py`)
Responsável pela extração e processamento de texto de arquivos PDF:
- Leitura de arquivos PDF usando PyPDF
- Extração de texto com tratamento de erros
- Divisão inteligente em chunks com sobreposição configurável
- Processamento em lote de múltiplos documentos

#### EmbeddingGenerator (`backend/embedding_generator.py`)
Gerencia a geração de embeddings usando a API OpenAI:
- Integração com o modelo text-embedding-ada-002
- Processamento em lote para eficiência
- Tratamento de erros e retry automático
- Limpeza e normalização de texto

#### PineconeManager (`backend/pinecone_manager.py`)
Gerencia todas as operações com o Pinecone:
- Criação e configuração automática de índices
- Inserção (upsert) de vetores com metadados
- Busca por similaridade com filtros
- Estatísticas e monitoramento do índice

#### ConversationalAssistant (`backend/assistant.py`)
Classe principal que integra todos os componentes:
- Orquestração do fluxo completo de processamento
- Geração de respostas contextualizadas usando GPT-4
- Gerenciamento de sessões e estado
- Interface unificada para o frontend

### Frontend

#### Interface Streamlit (`frontend/app.py`)
Interface web completa com:
- Dashboard de status do sistema
- Área de upload e gerenciamento de documentos
- Interface de chat com histórico
- Visualização de fontes e metadados

## Fluxo de Dados

### 1. Indexação de Documentos
```
PDF Upload → Extração de Texto → Chunking → Geração de Embeddings → Indexação no Pinecone
```

### 2. Consulta e Resposta
```
Pergunta do Usuário → Embedding da Pergunta → Busca no Pinecone → Recuperação de Contexto → Geração de Resposta (GPT-4) → Exibição para o Usuário
```

## Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- Conta OpenAI com API key
- Conta Pinecone com API key

### Instalação Manual

1. **Crie um ambiente virtual**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou
   .venv\Scripts\activate  # Windows
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas chaves de API
   ```

4. **Crie o diretório de PDFs**
   ```bash
   mkdir pdfs
   ```

4. **Execute os testes**
   ```bash
   python test.py
   ```

5. **Inicie a aplicação**
   ```bash
   python run.py
   ```

## Uso da Aplicação

### 1. Acesso à Interface
Após iniciar a aplicação, acesse: `http://localhost:8501`

### 2. Upload de Documentos
- Navegue até a aba "Documentos"
- Faça upload de arquivos PDF usando o componente de upload
- Clique em "Indexar Documentos" para processar os arquivos

### 3. Conversação
- Navegue até a aba "Chat"
- Digite suas perguntas na caixa de texto
- Clique em "Perguntar" para obter respostas
- Visualize as fontes consultadas expandindo "Fontes consultadas"

### 4. Monitoramento
- Verifique o status do sistema na barra lateral
- Monitore o número de vetores indexados
- Acompanhe a ocupação do índice Pinecone

## Configurações Avançadas

### Variáveis de Ambiente Opcionais

```env
# Configurações de processamento
PDF_DIRECTORY=pdfs
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Configurações de busca
DEFAULT_TOP_K=5
SIMILARITY_THRESHOLD=0.7
```

### Personalização de Modelos

Para usar modelos diferentes, edite o arquivo `backend/config.py`:

```python
class Config:
    OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
    OPENAI_CHAT_MODEL = "gpt-4"  # ou "gpt-3.5-turbo"
```

## Estrutura do Projeto

```
assistant_project/
├── backend/
│   ├── __init__.py
│   ├── assistant.py          # Classe principal do assistente
│   ├── config.py            # Configurações centralizadas
│   ├── embedding_generator.py # Geração de embeddings
│   ├── pdf_processor.py     # Processamento de PDFs
│   └── pinecone_manager.py  # Gerenciamento do Pinecone
├── frontend/
│   └── app.py              # Interface Streamlit
├── pdfs/                   # Diretório para arquivos PDF
├── .env.example           # Exemplo de variáveis de ambiente
├── .venv/                 # Ambiente virtual Python
├── requirements.txt       # Dependências Python
├── run.py                # Script principal de execução
├── setup.sh              # Script de configuração
├── test.py               # Testes do sistema
└── README.md             # Esta documentação
```

## Solução de Problemas

### Erro de Importação do Pinecone
Se encontrar erro relacionado ao `pinecone-client`, execute:
```bash
pip uninstall pinecone-client -y
pip install pinecone
```

### Erro de Variáveis de Ambiente
Verifique se o arquivo `.env` está configurado corretamente:
```bash
python test.py
```

### Problemas de Conectividade
- Verifique sua conexão com a internet
- Confirme se as chaves de API estão válidas
- Teste a conectividade com os serviços:
  ```bash
  curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
  ```

### Erro de Permissões
No Linux/Mac, certifique-se de que o script setup.sh tem permissões de execução:
```bash
chmod +x setup.sh
```

## Limitações e Considerações

### Limitações Técnicas
- **Tamanho de Documentos**: Documentos muito grandes podem exceder limites de tokens
- **Idioma**: Otimizado para português e inglês
- **Formato**: Suporta apenas arquivos PDF

### Limitações de API
- **OpenAI**: Sujeito a limites de rate e custos por uso
- **Pinecone**: Limitado pelo plano escolhido (gratuito tem restrições)

### Considerações de Segurança
- Mantenha suas chaves de API seguras
- Não compartilhe o arquivo `.env`
- Use HTTPS em produção

## Desenvolvimento e Contribuição

### Executando Testes
```bash
python test.py
```

### Adicionando Novos Recursos
1. Implemente a funcionalidade no módulo apropriado
2. Adicione testes correspondentes
3. Atualize a documentação
4. Teste a integração completa

### Estrutura de Testes
- Testes de importação de módulos
- Validação de variáveis de ambiente
- Testes de funcionalidades básicas
- Verificação de diretórios e arquivos

## Referências e Tecnologias

### Principais Dependências
- **OpenAI**: API para embeddings e geração de texto
- **Pinecone**: Banco de dados vetorial para busca semântica
- **Streamlit**: Framework para interface web
- **LangChain**: Framework para aplicações LLM
- **PyPDF**: Biblioteca para processamento de PDFs

### Documentação Oficial
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)

## Licença

Este projeto é fornecido como está, para fins educacionais e de demonstração. Consulte as licenças das dependências individuais para uso comercial.

## Suporte

Para problemas ou dúvidas:
1. Verifique a seção de Solução de Problemas
2. Execute `python test.py` para diagnóstico
3. Consulte a documentação das APIs utilizadas
4. Verifique os logs da aplicação para erros específicos

---

**Desenvolvido com ❤️ usando Python, OpenAI, Pinecone e Streamlit**

