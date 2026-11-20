import os
import time
from datetime import datetime

import psutil

LOG_FILE = os.getenv("LOG_FILE", "/app/logs/metrics.log")
INTERVAL = int(os.getenv("INTERVAL", "10"))  # seconds


def collect_metrics():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    uptime_sec = int(time.time() - psutil.boot_time())
    uptime = f"{uptime_sec // 3600}h {(uptime_sec % 3600) // 60}m"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"{timestamp} | CPU: {cpu}% | Memory: {mem}% | "
        f"Disk: {disk}% | Uptime: {uptime}"
    )


def main():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    while True:
        record = collect_metrics()
        with open(LOG_FILE, "a") as f:
            f.write(record + "\n")
        print(record, flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
