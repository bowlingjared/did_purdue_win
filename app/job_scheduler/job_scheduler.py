from datetime import datetime, timedelta

class JobScheduler:
    def __init__(self, scheduler, team_data_client):
        self.scheduler = scheduler
        self.team_data_client = team_data_client

    def generate_graph(self):
        """
        Get the latest game data and generate the win state, score, and win loss graph
        """
        latest_game = self.team_data_client.get_latest_game()
        is_latest_win = self.team_data_client.check_team_win(latest_game)
        with open("app/static/is_win.txt", "w") as file:
            file.write(str(is_latest_win))
        
        score = self.team_data_client.get_game_score(latest_game)
        with open("app/static/score.txt", "w") as file:
            file.write(score)
        
        opponent = self.team_data_client.get_opponent(latest_game)
        with open("app/static/opponent.txt", "w") as file:
            file.write(opponent)
        
        image_data = self.team_data_client.generate_wl_graph()
        image_data.save('app/static/win_loss.png', format='png')

    def schedule_generate_graph_job(self, update_time):
        """
        generate a graph generation job for the scheduler for the given time
        """
        self.scheduler.add_job(
            id=f'regenerate_graph_{update_time}', 
            func=self.generate_graph, 
            trigger='date', 
            run_date=datetime.fromisoformat(update_time)
        )

    def generate_graph_jobs(self, start_up=False):
        """
        schedule graph jobs for all upcoming games
        """
        #do a job now if we are just booting up the sever
        if start_up:
            self.scheduler.add_job(
                id='regenerate_graph_startup', 
                func=self.generate_graph, 
                trigger='date', 
                run_date=datetime.now()
            )
        
        update_times = self.team_data_client.get_update_times()
        
        for update_time in update_times:
            self.schedule_generate_graph_job(update_time)
        
        # schedule another job to check for more games 24 hours after last game or 24 hours from now
        if update_times:
            latest_update = max(update_times)
            graph_job_update_time = datetime.fromisoformat(latest_update) + timedelta(hours=24)
            self.scheduler.add_job(id=f'regenerate_graph_jobs_{graph_job_update_time}', func=self.generate_graph_jobs, kwargs={'start_up': False}, trigger='date', run_date=graph_job_update_time)
        else:
            graph_job_update_time = datetime.now() + timedelta(hours=24)
            self.scheduler.add_job(id=f'regenerate_graph_jobs_{graph_job_update_time}', func=self.generate_graph_jobs, kwargs={'start_up': False}, trigger='date', run_date=graph_job_update_time)
