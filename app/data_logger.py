import csv
import os
from datetime import datetime

def log_user_data(mood, sleep, water, message, path="user_data.csv"):
    file_exists = os.path.isfile(path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(path, mode="a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "mood", "sleep", "water", "message"])
        writer.writerow([now, mood, sleep, water, message])
