from flask import Flask
import os
import subprocess
from datetime import datetime
import pytz

app = Flask(__name__)

@app.route('/htop')
def htop():

    full_name = "Yuktha Mukhi Nadella"

    try:
        username = os.getlogin()
    except OSError:
        username = os.environ.get('USER', 'unknown')

    tz_IST = pytz.timezone('Asia/Kolkata')
    server_time = datetime.now(tz_IST).strftime("%Y-%m-%d %H:%M:%S")

    try:
        top_output = subprocess.check_output(['top', '-b', '-n', '1']).decode('utf-8')
        top_lines = "\n".join(top_output.splitlines()[:10])
    except Exception as e:
        top_lines = f"Error running top: {str(e)}"

    return f"""
    <h1>HTOP Endpoint</h1>
    <p><strong>Name:</strong> {full_name}</p>
    <p><strong>Username:</strong> {username}</p>
    <p><strong>Server Time (IST):</strong> {server_time}</p>
    <pre>{top_lines}</pre>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
