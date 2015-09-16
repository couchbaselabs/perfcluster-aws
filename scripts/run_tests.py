import os
import subprocess
import sys
import time
from optparse import OptionParser

usage = "usage: %run_tests.py -u <number_of_pushers> -d <number_of_pullers>"

parser = OptionParser(usage=usage)

parser.add_option("-d", "--number-pullers",
                  action="store", type="string", dest="number_pullers", default=0,
                  help="number of pullers")


parser.add_option("-u", "--number-pushers",
                  action="store", type="int", dest="number_pushers", default=7500,
                  help="number of pushers")

arg_parameters = sys.argv[1:]

(opts, args) = parser.parse_args(arg_parameters)

NUMBER_PULLERS = opts.number_pullers
NUMBER_PUSHERS = opts.number_pushers

print ">>> Starting gatling with {0} pullers and {1} pushers".format(NUMBER_PULLERS, NUMBER_PUSHERS)

os.chdir("../ansible/playbooks")

# Configure gatling
subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "configure-gatling.yml"])

# Run Gatling
subprocess.call([
    "ansible-playbook", "-l", os.path.expandvars("$KEYNAME"),
    "run-gatling-theme.yml",
    "--extra-vars", "number_of_pullers={0} number_of_pushers={1}".format(NUMBER_PULLERS, NUMBER_PUSHERS)
])