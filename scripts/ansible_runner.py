import os
import subprocess

# TODO provide a way to specify inventory (perhaps local or private vm endpoints)


def run_ansible_playbook(script_name, extra_vars=""):
    if extra_vars != "":
        subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), script_name, "--extra-vars", extra_vars])
    else:
        subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), script_name])
