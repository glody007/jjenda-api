import os
from flask import Flask, current_app, send_file
from flask_bcrypt import Bcrypt
from .models import init_db

from .api import api_bp
from .client import client_bp

app = Flask(__name__, static_folder='../dist/static')
bcrypt = Bcrypt(app)
app.register_blueprint(api_bp)
app.register_blueprint(client_bp)

from .config import Config
app.logger.info('>>> {}'.format(Config.FLASK_ENV))

@app.route('/')
def index_client():
    dist_dir = current_app.config['DIST_DIR']
    entry = os.path.join(dist_dir, 'index.html')
    return send_file(entry)

def get_app():
    with app.app_context():
        init_db()
    return app
