import subprocess
import sys
from optparse import OptionParser

usage = "usage: python teardown_cluster.py -n <stack_name>"

parser = OptionParser(usage=usage)

parser.add_option("-n", "--stackname",
                  action="store", type="string", dest="stack_name", default="default",
                  help="stackname of cloudformation cluster to delete")

arg_parameters = sys.argv[1:]

(opts, args) = parser.parse_args(arg_parameters)
STACKNAME = opts.stack_name

subprocess.call([
    "aws", "cloudformation", "delete-stack",
    "--stack-name", STACKNAME, "--region", "us-east-1"
])
