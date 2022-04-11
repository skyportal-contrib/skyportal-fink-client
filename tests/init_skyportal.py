import os
import subprocess
import time

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
skyportal_dir = basedir + "/../skyportal"

web_client = subprocess.Popen(
        ['make', 'run'], cwd=basedir, preexec_fn=os.setsid
    )
time.sleep(30)
