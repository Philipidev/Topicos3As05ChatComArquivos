# streamlit_app.py
import sys
import os

# Garante que os módulos backend sejam encontrados
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Agora chama a interface diretamente
from frontend import app  # frontend/app.py será executado
