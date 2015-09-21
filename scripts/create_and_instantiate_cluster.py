import sys
import os
import subprocess
from optparse import OptionParser

import cloudformation_template

usage = "usage: %create_and_instantiate_cloud -n <cluster_name> -s <number_couchbase_servers> -g <number_sync_gateways> -l <number_gateloads>"
parser = OptionParser(usage=usage)

parser.add_option("-n", "--stackname",
                  action="store", type="string", dest="stackname", default="default",
                  help="name for your cluster")

parser.add_option("-s", "--num-servers",
                  action="store", type="int", dest="num_servers", default=3,
                  help="number of couchbase server instances")

parser.add_option("-t", "--server-type",
                  action="store", type="string", dest="server_type", default="m3.medium",
                  help="EC2 instance type for couchbase server")

parser.add_option("-g", "--num-sync-gateways",
                  action="store", type="int", dest="num_sync_gateways", default=1,
                  help="number of sync_gateway instances")

parser.add_option("-u", "--sync-gateway-type",
                  action="store", type="string", dest="sync_gateway_type", default="m3.medium",
                  help="EC2 instance type for sync_gateway type")

parser.add_option("-l", "--num-gatlings",
                  action="store", type="int", dest="num_gatlings", default=1,
                  help="number of gatling instances")

parser.add_option("-v", "--gatling-type",
                  action="store", type="string", dest="gatling_type", default="m3.medium",
                  help="EC2 instance type for gatling type")

arg_parameters = sys.argv[1:]

(opts, args) = parser.parse_args(arg_parameters)

STACKNAME = opts.stackname

NUM_COUCHBASE_SERVERS = opts.num_servers
SERVER_TYPE = opts.server_type

NUM_SYNC_GATEWAYS = opts.num_sync_gateways
SYNC_GATEWAY_TYPE = opts.sync_gateway_type

NUM_GATLINGS = opts.num_gatlings
GATLING_TYPE = opts.gatling_type

print ">>> Provisioning cluster... "

print ">>> Couchbase Server Instances: {}".format(NUM_COUCHBASE_SERVERS)
print ">>> Couchbase Server Type: {}".format(SERVER_TYPE)

print ">>> Sync Gateway Instances:     {}".format(NUM_SYNC_GATEWAYS)
print ">>> Sync Gateway Type:     {}".format(SYNC_GATEWAY_TYPE)

print ">>> Gatling Instances:          {}".format(NUM_GATLINGS)
print ">>> Gatling Type:          {}".format(GATLING_TYPE)

print ">>> Generating Cloudformation Template"
json = cloudformation_template.gen_template(
    NUM_COUCHBASE_SERVERS,
    SERVER_TYPE,
    NUM_SYNC_GATEWAYS,
    SYNC_GATEWAY_TYPE,
    NUM_GATLINGS,
    GATLING_TYPE
)

TEMPLATE_FILENAME = "cloudformation_template.json"

template_file = open(TEMPLATE_FILENAME, 'w')
template_file.write(json)
template_file.close()

print ">>> Creating cluster on AWS"

key = os.path.expandvars("$AWS_KEY")

subprocess.call([
    "aws", "cloudformation", "create-stack",
    "--stack-name", STACKNAME,
    "--region", "us-east-1",
    "--template-body", "file://{}".format(TEMPLATE_FILENAME),
    "--parameters", "ParameterKey=KeyName,ParameterValue={}".format(key)
])
