import cfbd
from cfbd.rest import ApiException
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-interactive image generation
import matplotlib.pyplot as plt
import io
import base64
import PIL.Image

class TeamGameData:
    #
    def __init__(self, team_name, current_time=datetime.now()):
        #Load api key from env file
        if os.path.exists('app\purdue_data_client\cfdb_api.env'):
            load_dotenv(rf'app\purdue_data_client\cfdb_api.env')
        self.api_key = os.getenv("CFBD_API_KEY")
        
        self.configuration = cfbd.Configuration()
        self.configuration.api_key['Authorization'] = f'Bearer {self.api_key}'
        self.api_instance = cfbd.GamesApi(cfbd.ApiClient(self.configuration))
        
        #Set current year
        self.current_year = current_time.year
        self.current_date = current_time.isoformat()
        
        self.team_name = team_name

    def get_next_game(self):
        """
        Fetches the next scheduled game
        Returns the next game if scheduled, otherwise 'TBD'.
        """
        try:
            # Get the current date
            current_date = datetime.now().date()
            games = self.api_instance.get_games(year=self.current_year, team=self.team_name)

            # Filter games to find those that have already occurred
            future_games = [game for game in games if datetime.fromisoformat(game.start_date).date() > current_date]

            #Return code if no future games scheduled
            if len(future_games) <= 0:
                return 'TBD'

            # Find the next earliest game
            most_recent_game = min(future_games, key=lambda x: x.start_date)

            return most_recent_game
        except ApiException as e:
            print(f"Exception when calling GamesApi->get_games: {e}")
            return None
        
    def get_latest_game(self):
        """
        Fetches the next scheduled game
        Returns the next game if scheduled, otherwise 'TBD'.
        """
        try:
            # Get the current date
            current_date = datetime.now().date()

            # Fetch all games for Purdue
            games = self.api_instance.get_games(year=self.current_year, team=self.team_name)

            # Filter for games that have already happened AND are completed
            past_games = [game for game in games if datetime.fromisoformat(game.start_date).date() <= current_date and game.completed == True]

            if len(past_games) <= 0:
                previous_year = self.current_year - 1
                while len(past_games) <= 0:
                        # Fetch all games for Purdue from a previous year, all guarnteed to be before current date
                        past_games = self.api_instance.get_games(year=previous_year, team=self.team_name)
                print("No past games found.")
                return None

            # Find the most recent game
            most_recent_game = max(past_games, key=lambda x: x.start_date)

            return most_recent_game
        
        except ApiException as e:
            print(f"Exception when calling GamesApi->get_games: {e}")
            return None
        
    def get_upcoming_games(self):
        try:
            games = self.api_instance.get_games(year=self.current_year, team=self.team_name)
            upcoming_games = [game for game in games if game.start_date > self.current_date]
            return upcoming_games
        except ApiException as e:
            print(f"Exception when calling GamesApi->get_games: {e}")
            return []

    def get_recent_games(self):
        """
        API call to get all games played this season
        """
        try:
            games = self.api_instance.get_games(year=self.current_year, team=self.team_name)
            past_games = [game for game in games if game.start_date <= self.current_date and game.completed == True]
            return past_games
        except ApiException as e:
            print(f"Exception when calling GamesApi->get_games: {e}")
            return []
    def check_team_win(self, game):
        """
        Takes in API call for any given game and check if Purdue won
        Returns boolean, if Purdue did not play in this game
        """
        home_team = game.home_team
        away_team = game.away_team
        home_score = game.home_points
        away_score = game.away_points
    
        # Check if Purdue was home, away, or did not play
        if home_team == self.team_name:
            return home_score > away_score
        elif away_team == self.team_name:
            return away_score > home_score
        else:
            return False  # Purdue is not in this game
        
    def check_team_win_most_recent(self):
        """
        Query the latest game and check if Purdue won
        Returns boolean
        """
        return self.check_team_win(self.get_latest_game())
    
    def generate_wl_graph(self):
        # Create a list of the integers
        games = self.get_recent_games()
        wins = 0
        losses = 0
        for game in games:
            if self.check_team_win(game):
                wins = wins + 1
            else:
                losses = losses + 1
            
        data = [wins, losses]

        # Create a bar chart
        plt.bar(["Wins", "Losses"], data, color=['yellow', 'black'])

        # Add labels and title
        plt.title("Wins Losses")

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)

        # Create a PIL Image object from the buffer
        image_data = PIL.Image.open(img_buffer)
        
        return image_data
    
    def get_update_times(self):
        """
        Query upcoming games to find out when i need to schedule graph updates
        list of date time objects
        """
        game_times = []
        twelve_hours = timedelta(hours=12)
        games = self.get_upcoming_games()
        for game in games:
            datetime.fromisoformat(game.start_date)+twelve_hours
            game_times.append(game.start_date)
        return game_times
    def get_game_score(self, game):
        """
        Return a string of the score of any given game call
        """
        scores = [int(game.home_points), int(game.away_points)]
        scores.sort(reverse=True)
        return f"{scores[0]}-{scores[1]}"
        
        
                
    
        
