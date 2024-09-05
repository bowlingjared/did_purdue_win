from app.purdue_data_client.purdue_client import TeamGameData
from flask import current_app as app
from flask import render_template
from flask import url_for
purdue_client = TeamGameData(team_name='Purdue')

@app.route('/')
def home():
    if purdue_client.check_team_win_most_recent:
        image_url = url_for('static', filename='test.png')
        return render_template('win.html', image_url=image_url)