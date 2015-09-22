import os
import subprocess

os.chdir("../ansible/playbooks")

subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "kill-gateload.yml"])
