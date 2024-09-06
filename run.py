from app import create_app
from app.purdue_data_client.purdue_client import TeamGameData
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=10000)