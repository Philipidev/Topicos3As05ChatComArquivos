# streamlit_app.py

import sys
import os

# Garante que o backend seja encontrado nos imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

# Executa diretamente a interface Streamlit do app
exec(open("frontend/app.py").read())
