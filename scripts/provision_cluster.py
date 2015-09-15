import os
import subprocess
import sys
import time
from optparse import OptionParser

usage = """usage: %provision_cluster -s <couchbase_server_version> -g <sync_gateway_version>
        usage: %provision_cluster -s <couchbase_server_version> -c -b <branch_to_checkout>"""

parser = OptionParser(usage=usage)

parser.add_option("-s", "--server-version",
                  action="store", type="string", dest="server_version", default="3.1.0",
                  help="server binary version to download")

parser.add_option("-g", "--sync-gateway-version",
                  action="store", type="string", dest="sync_gateway_version", default="1.1.1",
                  help="sync_gateway binary version to download")

parser.add_option("-c", "--build-from-source",
                  action="store_true", dest="build_from_source", default=False,
                  help="build sync_gateway from source")

parser.add_option("-b", "--branch",
                  action="store", type="string", dest="source_branch", default="master",
                  help="sync_gateway branch to checkout and build")

arg_parameters = sys.argv[1:]

(opts, args) = parser.parse_args(arg_parameters)

COUCHBASE_SERVER_VERSION = opts.server_version
SYNC_GATEWAY_VERSION = opts.sync_gateway_version
BUILD_FROM_SOURCE = opts.build_from_source
BRANCH = opts.source_branch

current_time = time.time()
step_times = {}

def logtime(id):
    global current_time
    step_times[id] = time.time() - current_time
    current_time = time.time()

os.chdir("../ansible/playbooks")

subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "install-go.yml"])
logtime("install-go.yml")

subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "install-couchbase-server-stable.yml", "--extra-vars", "couchbase_server_centos_ee_version={}".format(COUCHBASE_SERVER_VERSION)])
logtime("install-couchbase-server-stable.yml")

if BUILD_FROM_SOURCE:
    print "Build from source"
    subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "build-sync-gateway-source.yml", "--extra-vars", "branch={}".format(BRANCH)])
    logtime("build-sync-gateway-source.yml")
else:
    print "Build stable"
    subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "install-sync-gateway-release.yml", "--extra-vars", "couchbase_sync_gateway_centos_ee_version={}".format(SYNC_GATEWAY_VERSION)])
    logtime("build-sync-gateway-source.yml")

subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "install-sync-gateway-service.yml"])
logtime("install-sync-gateway-service.yml")

subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "install-splunkforwarder.yml"])
logtime("install-splunkforwarder.yml")

for k in step_times:
    print "[{0}] = {1}".format(k, step_times[k])

