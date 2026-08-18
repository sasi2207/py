import sys
import os

# Server directory path
sys.path.insert(0, os.path.dirname(__file__))

# Convert FastAPI (ASGI) to WSGI using a2wsgi
from a2wsgi import ASGIMiddleware
from main import app

application = ASGIMiddleware(app)