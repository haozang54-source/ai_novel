import sys
from pathlib import Path
from flask import Flask
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from novel_web.backend.config import Config
from novel_web.backend.database import db
from novel_web.backend.routes import register_routes

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, origins=app.config['CORS_ORIGINS'])
db.init_app(app)

register_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
