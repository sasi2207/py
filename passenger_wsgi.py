import os
import sys

# 1. Add current project directory to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# 2. Load .env environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(CURRENT_DIR, ".env"))

# 3. Import FastAPI instance from main.py
from main import app

# 4. Wrap ASGI (FastAPI) into WSGI (cPanel Passenger)
from a2wsgi import ASGIMiddleware

application = ASGIMiddleware(app)