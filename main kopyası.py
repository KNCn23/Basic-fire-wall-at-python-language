from flask import Flask, request, abort
import time
from collections import Counter
import os
import shutil

app = Flask(__name__)

BANNED_IPS = set()
REQUEST_COUNTER = Counter()
TIME_WINDOW = 10
MAX_REQUESTS = 100
BANNED_IPS_FILE_PATH = os.path.expanduser('~/Desktop/banned_ips.txt')  # Masaüstündeki dosya yolu

def rate_limiter(func):
    def wrapper(*args, **kwargs):
        global REQUEST_COUNTER

        current_time = time.time()
        old_times = [t for t in REQUEST_COUNTER if t < current_time - TIME_WINDOW]
        for t in old_times:
            del REQUEST_COUNTER[t]

        ip = request.remote_addr
        REQUEST_COUNTER[current_time, ip] += 1

        total_requests = sum(REQUEST_COUNTER[t, ip] for t in REQUEST_COUNTER if ip in t)
        if total_requests > MAX_REQUESTS and ip not in BANNED_IPS:
            BANNED_IPS.add(ip)
            with open(BANNED_IPS_FILE_PATH, 'a') as file:
                file.write(ip + '\n')
            abort(403)

        return func(*args, **kwargs)
    return wrapper

@app.route('/')
@rate_limiter
def index():
    return "Merhaba Dünya!"

def move_to_trash(path):
    trash = os.path.expanduser('~/.Trash')
    shutil.move(path, trash)

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        if os.path.exists(BANNED_IPS_FILE_PATH):
            move_to_trash(BANNED_IPS_FILE_PATH)
