from flask import Flask
from sqlalchemy.orm import sessionmaker

from api.database.db import engine
from api.database.models.base import Base
from api.utils.import_db import import_sql_file
from routes import bp

# Create all tables in the database
Base.metadata.create_all(engine)

# Import SQL data from dump files
# try:
#     import_sql_file("database/dump/airports.sql")
# except FileNotFoundError as e:
#     print(f"Warning: {e}")

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
