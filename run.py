from app import create_app
from app.purdue_data_client.purdue_client import TeamGameData
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta


app = create_app()

# initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

purdue_client = TeamGameData(team_name='Purdue')

def generate_graph():
    image_data = purdue_client.generate_wl_graph()
    image_data.save('app/static/test.png', format='png')

def generate_graph_jobs(start_up=False):
    if start_up == True:
        scheduler.add_job(id='regenerate_graph_startup', func=generate_graph, trigger='date', run_date=datetime.now())
    update_times = purdue_client.get_update_times()
    for update_time in update_times:
        generate_graph_job(update_time)
    if update_times:
        latest_update = max(update_times)
        graph_job_update_time = datetime.fromisoformat(latest_update) + timedelta(hours=24)
        scheduler.add_job(id=f'regenerate_graph_jobs_{graph_job_update_time}', func=generate_graph_jobs, kwargs={'start_up': False}, trigger='date', run_date=graph_job_update_time)
    else:
        graph_job_update_time = datetime.now() + timedelta(hours=24)
        scheduler.add_job(id=f'regenerate_graph_jobs_{graph_job_update_time}', func=generate_graph_jobs, kwargs={'start_up': False}, trigger='date', run_date=graph_job_update_time)
        
        
def generate_graph_job(update_time):
    scheduler.add_job(id=f'regenerate_graph_{update_time}', func=generate_graph, trigger='date', run_date=datetime.fromisoformat(update_time))
    


if __name__ == "__main__":
    generate_graph_jobs(start_up=True)
    app.run(debug=True)