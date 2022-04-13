import os
import subprocess
import time

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
skyportal_dir = basedir + "/../skyportal"

cmd = subprocess.Popen(["make", "run"], cwd=skyportal_dir, preexec_fn=os.setsid)

time.sleep(60)

cmd = subprocess.Popen(
    ["make", "load_demo_data"], cwd=skyportal_dir, preexec_fn=os.setsid
)

time.sleep(30)
