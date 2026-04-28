import os
from sqlalchemy import create_engine

# Get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construct absolute path to the database
DATABASE_PATH = os.path.join(BASE_DIR, 'sqlite', 'sqlite.db')

# Ensure the directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# Create engine with absolute path
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=True)