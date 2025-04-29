import subprocess
import sys
import time

scripts = [
    "backend.processors.gfw.vessels_api",
    "backend.processors.gfw.loitering_api"
]

while True:
    for script in scripts:
        print(f"\nRunning {script} ...")
        subprocess.run([sys.executable, "-m", script])
    
    print("\nWaiting 300 seconds before next run...")
    time.sleep(300)
