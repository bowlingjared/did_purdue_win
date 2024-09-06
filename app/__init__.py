from flask import Flask
from flask import g
from app.purdue_data_client.purdue_client import TeamGameData
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta
from app.job_scheduler.job_scheduler import JobScheduler


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    purdue_client = TeamGameData(team_name='Purdue') 

    with app.app_context():
        
        from . import routes
        
        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.start()
        job_scheduler = JobScheduler(scheduler, purdue_client)
        job_scheduler.generate_graph_jobs()
        
        return app