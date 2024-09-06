from app.purdue_data_client.purdue_client import TeamGameData
from flask import current_app as app
from flask import render_template
from flask import url_for
from flask import g
purdue_client = TeamGameData(team_name='Purdue')

@app.route('/')
def home():
    image_url = url_for('static', filename='win_loss.png')
    with open('app/static/score.txt', 'r') as file:
        score = file.read().strip()
    with open('app/static/opponent.txt', 'r') as file:
        opponent = file.read().strip()
    with open('app/static/is_win.txt', 'r') as file:
        is_win = file.read().strip()
    
    if is_win:
        return render_template('win.html', image_url=image_url, score=score, opponent=opponent)
    else:
        return render_template('loss.html', image_url=image_url, score=score, opponent=opponent)