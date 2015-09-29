import os
import subprocess

def kill_gateload():
    os.chdir("../ansible/playbooks")
    subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "kill-gateload.yml"])

if __name__ == "__main__":
    kill_gateload()

