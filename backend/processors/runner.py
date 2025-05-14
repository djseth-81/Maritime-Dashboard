import subprocess
import sys
import time
from threading import Thread

scripts = [
    "backend.processors.coop.alerts_api",
    "backend.processors.coop.met_api",
    "backend.processors.gfw.encounters_api",
    "backend.processors.gfw.fishing_api",
    "backend.processors.gfw.loitering_api",
    "backend.processors.gfw.ports_api",
    "backend.processors.gfw.transponder_api",
    "backend.processors.gfw.vessels_api",
    "backend.processors.nws.alerts_api",
    "backend.processors.nws.met_api"
]

def scraper(script):
    print(f"\nRunning {script} ...")
    subprocess.run([sys.executable, "-m", script])
    print("\nWaiting 300 seconds before next run...")
    time.sleep(300)

if __name__ == "__main__":
    while True:
        for script in scripts:
            thread = Thread(target=scraper, args=(script,), daemon=True)
            thread.start()
        time.sleep(300)
