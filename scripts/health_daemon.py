"""
NeuroStudy 24/7 Watchdog Service Daemon
"""
import time
import urllib.request
import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "data" / "uptime_sla.log"

def check_service(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NeuroStudyWatchdog/2.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False

def main():
    while True:
        now = datetime.datetime.now().isoformat()
        st_ok = check_service("http://localhost:8501")
        status = "ONLINE (200 OK)" if st_ok else "OFFLINE"
        with open(LOG_FILE, "a") as f:
            f.write(f"[{now}] Streamlit: {status}\n")
        time.sleep(30)

if __name__ == "__main__":
    main()
