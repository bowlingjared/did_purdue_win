from flask import Flask
from flask import g
from app.purdue_data_client.purdue_client import TeamGameData

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  

    with app.app_context():
        
        from . import routes

        return app