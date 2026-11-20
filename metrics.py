import os
import time
from datetime import datetime

import boto3
import psutil

LOG_FILE = os.getenv("LOG_FILE", "/app/logs/metrics.log")
INTERVAL = int(os.getenv("INTERVAL", "10"))  # seconds
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY", "metrics.log")
UPLOAD_EVERY = int(os.getenv("UPLOAD_EVERY", "60"))  # seconds


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


def upload_to_s3(s3):
    try:
        s3.upload_file(LOG_FILE, S3_BUCKET, S3_KEY)
        print(f"Uploaded to s3://{S3_BUCKET}/{S3_KEY}", flush=True)
    except Exception as e:
        print(f"S3 upload failed: {e}", flush=True)


def main():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    s3 = boto3.client("s3") if S3_BUCKET else None
    last_upload = 0
    while True:
        record = collect_metrics()
        with open(LOG_FILE, "a") as f:
            f.write(record + "\n")
        print(record, flush=True)
        if s3 and time.time() - last_upload >= UPLOAD_EVERY:
            upload_to_s3(s3)
            last_upload = time.time()
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
