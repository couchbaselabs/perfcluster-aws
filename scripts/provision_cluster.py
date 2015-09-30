import os
import subprocess
import sys
import urlparse
import httplib
from optparse import OptionParser

import install_sync_gateway
import install_couchbase_server

from install_couchbase_server import CouchbaseServerConfig
from install_sync_gateway import SyncGatewayConfig

import ansible_runner

# TODO Add SG package

def provision_cluster(couchbase_server_config, sync_gateway_config):

    print ">>> Validating..."

    if not couchbase_server_config.is_valid():
        print "Invalid server provisioning configuration. Exiting ..."
        sys.exit(1)

    if not sync_gateway_config.is_valid():
        print "Invalid sync_gateway provisioning configuration. Exiting ..."
        sys.exit(1)

    print ">>> Provisioning cluster..."

    # Get server base url and package name
    server_base_url, server_package_name = couchbase_server_config.server_base_url_and_package()

    print ">>> Server package: {0}/{1}".format(server_base_url, server_package_name)

    if sync_gateway_config.build_from_source:
        print ">>> Building sync_gateway: branch={}".format(sync_gateway_config.sync_gateway_branch)
    else:
        # TODO
        print ">>> sync_gateway package"

    print ">>> Using sync_gateway config: {}".format(sync_gateway_config.sync_gateway_config_path)

    os.chdir("../ansible/playbooks")

    # Install dependencies
    ansible_runner.run_ansible_playbook("install-go.yml")

    # Install server package
    install_couchbase_server.install_couchbase_server(couchbase_server_config)

    # Install sync_gateway
    install_sync_gateway.install_sync_gateway(sync_gateway_config)

    ansible_runner.run_ansible_playbook("install-splunkforwarder.yml")


if __name__ == "__main__":
    usage = """usage: python provision_cluster.py
    --server-version=<server_version_number>
    --server-build=<server_build_number>
    --sync-gateway-version=<sync_gateway_version_number>
    --sync-gateway-build=<sync_gateway_build_number>
    --sync-gateway-config-file=<path_to_local_sync_gateway_config>

    or

    usage: python provision_cluster.py
    --server-version=<server_version_number>
    --server-build=<server_build_number>
    --build-sync-gateway
    --branch=<sync_gateway_branch_to_build>
    --sync-gateway-config-file=<path_to_local_sync_gateway_config>
    """

    parser = OptionParser(usage=usage)

    parser.add_option("", "--server-version",
                      action="store", type="string", dest="server_version", default="3.1.1",
                      help="server version to download")

    parser.add_option("", "--server-build",
                      action="store", type="string", dest="server_build",
                      help="server build to download")

    parser.add_option("", "--sync-gateway-version",
                      action="store", type="string", dest="sync_gateway_version",
                      help="sync_gateway version to download")

    parser.add_option("", "--sync-gateway-build",
                      action="store", type="string", dest="sync_gateway_build",
                      help="sync_gateway build to download")

    parser.add_option("", "--sync-gateway-config-file",
                      action="store", type="string", dest="sync_gateway_config_file", default="../ansible/playbooks/files/sync_gateway_config.json",
                      help="path to your sync_gateway_config file")

    parser.add_option("", "--build-sync-gateway",
                      action="store_true", dest="build_from_source", default=True,
                      help="build sync_gateway from source")

    parser.add_option("", "--branch",
                      action="store", type="string", dest="source_branch", default="master",
                      help="sync_gateway branch to checkout and build")

    arg_parameters = sys.argv[1:]

    (opts, args) = parser.parse_args(arg_parameters)

    server_config = CouchbaseServerConfig(
        version=opts.server_version,
        build_number=opts.server_build
    )

    sync_gateway_config = SyncGatewayConfig(
        version=opts.sync_gateway_version,
        build_number=opts.sync_gateway_build,
        build_from_source=opts.build_from_source,
        branch_to_build=opts.source_branch,
        sync_gateway_config_path=opts.sync_gateway_config_file
    )

    provision_cluster(
        couchbase_server_config=server_config,
        sync_gateway_config=sync_gateway_config
    )
