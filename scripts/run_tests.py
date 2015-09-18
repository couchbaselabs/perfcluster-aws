import os
import subprocess
import sys
from optparse import OptionParser

import generate_gateload_configs

usage = "usage: %run_tests.py -u <number_of_pushers> -d <number_of_pullers>"

parser = OptionParser(usage=usage)

parser.add_option("-d", "--number-pullers",
                  action="store", type="string", dest="number_pullers", default=0,
                  help="number of pullers")

parser.add_option("-u", "--number-pushers",
                  action="store", type="int", dest="number_pushers", default=7500,
                  help="number of pushers")

parser.add_option("-o", "--use-gateload",
                  action="store_true", dest="use_gateload", default=False,
                  help="flag to set to use gateload")

arg_parameters = sys.argv[1:]

(opts, args) = parser.parse_args(arg_parameters)

NUMBER_PULLERS = opts.number_pullers
NUMBER_PUSHERS = opts.number_pushers
USE_GATELOAD = opts.use_gateload

if USE_GATELOAD:
    print "Using Gateload"

    os.chdir("../ansible/playbooks")

    # Build gateload
    subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "build-gateload.yml"])

    # Generate gateload config
    generate_gateload_configs.main()

    # Start gateload
    subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), "start-gateload.yml"])

else:
    print "Using Gatling"
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
