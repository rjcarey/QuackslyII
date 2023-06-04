from flask import Flask
from threading import Thread
from datetime import datetime

app = Flask('')

@app.route('/')
def main():
    t = str(datetime.now()).split('.')[0]
    with open('log.txt', 'a') as f:
        f.write(f"pinged at {t}\n")
    return "up and running..."

def run():
    app.run(host="0.0.0.0", port=8000)

def keep_alive():
    server = Thread(target=run)
    server.start()
