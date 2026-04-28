from flask import Flask
from sqlalchemy.orm import sessionmaker

# IMPORTANT: Import ALL model classes here to ensure they're registered with SQLAlchemy
# This must happen BEFORE any database operations
from api.database.models import *

from api.database.db import engine
from api.utils.import_db import import_sql_file_direct
from routes import bp

# Create all tables based on SQLAlchemy models
# Base.metadata.create_all(engine)

# Import SQL data from dump files
# try:
#     import_sql_file_direct("database/dump/airports.sql")
#     print("✓ Data migration complete!")
#
# except FileNotFoundError as e:
#     print(f"Warning: {e}")
# except Exception as e:
#     print(f"Error during data import: {e}")
#     import traceback
#     traceback.print_exc()

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)

# Register blueprints from routes folder
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# Close session
session.close()
