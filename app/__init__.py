from flask import Flask
from flask import g
from app.purdue_data_client.purdue_client import TeamGameData
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta

purdue_client = TeamGameData(team_name='Purdue')

def generate_graph():
    latest_game = purdue_client.get_latest_game()
    is_latest_win = purdue_client.check_team_win(latest_game)
    with open("app/static/is_win.txt", "w") as file:
        file.write(str(is_latest_win))
    score = purdue_client.get_game_score(latest_game)
    with open("app/static/score.txt", "w") as file:
        file.write(score)
    opponent = purdue_client.get_opponent(latest_game)
    with open("app/static/opponent.txt", "w") as file:
        file.write(opponent)
    image_data = purdue_client.generate_wl_graph()
    image_data.save('app/static/win_loss.png', format='png')

def generate_graph_jobs(scheduler, start_up=False):
    if start_up == True:
        scheduler.add_job(id='regenerate_graph_startup', func=generate_graph, trigger='date', run_date=datetime.now())
    update_times = purdue_client.get_update_times()
    for update_time in update_times:
        generate_graph_job(scheduler=scheduler, update_time=update_time)
    if update_times:
        latest_update = max(update_times)
        graph_job_update_time = datetime.fromisoformat(latest_update) + timedelta(hours=24)
        scheduler.add_job(id=f'regenerate_graph_jobs_{graph_job_update_time}', func=generate_graph_jobs, kwargs={'scheduler': scheduler,'start_up': False}, trigger='date', run_date=graph_job_update_time)
    else:
        graph_job_update_time = datetime.now() + timedelta(hours=24)
        scheduler.add_job(id=f'regenerate_graph_jobs_{graph_job_update_time}', func=generate_graph_jobs, kwargs={'scheduler': scheduler,'start_up': False}, trigger='date', run_date=graph_job_update_time)
              
def generate_graph_job(update_time, scheduler):
    scheduler.add_job(id=f'regenerate_graph_{update_time}', func=generate_graph, trigger='date', run_date=datetime.fromisoformat(update_time))

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    purdue_client = TeamGameData(team_name='Purdue') 

    with app.app_context():
        
        from . import routes
        
        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.start()
        generate_graph_jobs(start_up=True, scheduler=scheduler)
        
        return app