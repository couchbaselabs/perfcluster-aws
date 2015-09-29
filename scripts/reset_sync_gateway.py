import os
import subprocess

def reset_sync_gateway():
    os.chdir("../ansible/playbooks")

    # Flush Couchbase server bucket-1 and bucket-2
    # Stop sync_gateway, delete sync_gateway logs, start sync_gateway
    subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "reset-sync-gateway.yml"])

if __name__ == "__main__":
    reset_sync_gateway()

