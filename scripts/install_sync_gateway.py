import sys
import os
from optparse import OptionParser

import ansible_runner


class SyncGatewayConfig:

    def __init__(self,
                 branch="",
                 version="",
                 build_number=-1,
                 sync_gateway_config_path="../ansible/playbooks/files/sync_gateway_config.json"):
        self.__version = version
        self.__build_number = build_number
        self.__branch = branch
        self.__sync_gateway_config_path = sync_gateway_config_path

    @property
    def version(self):
        return self.__version

    @property
    def build_number(self):
        return self.__build_number

    @property
    def branch(self):
        return self.__branch

    @property
    def sync_gateway_config_path(self):
        return self.__sync_gateway_config_path

    def __base_url_package_for_sync_gateway(self, version, build):
        base_url = "http://latestbuilds.hq.couchbase.com/couchbase-sync-gateway/release/{0}/{1}-{2}".format(version, version, build)
        package_name = "couchbase-sync-gateway-enterprise_{0}-{1}_x86_64.rpm".format(version, build)
        return base_url, package_name

    def sync_gateway_base_url_and_package(self):
        return self.__base_url_package_for_sync_gateway(self.__version, self.__build_number)

    def is_valid(self):
        if self.__version == "" and self.__branch == "":
            print "You must provide a version / build or branch to build for sync_gateway"
            return False
        if self.__branch != "" and (self.__version != "" or self.__build_number != -1):
            print "Specify --branch or --version, not both"
            return False
        if self.__version != "" and self.__build_number == -1:
            print "Must specify a build number for sync_gateway version"
            return False
        if not os.path.isfile(self.__sync_gateway_config_path):
            print "Could not find sync_gateway config file: {}".format(self.__sync_gateway_config_path)
            print "Try to use an absolute path."
            return False
        return True


def install_sync_gateway(sync_gateway_config):

    if not sync_gateway_config.is_valid():
        print "Invalid server provisioning configuration. Exiting ..."
        sys.exit(1)

    if sync_gateway_config.branch != "":
        print "Build from source with branch: {}".format(sync_gateway_config.sync_gateway_branch)
        ansible_runner.run_ansible_playbook("build-sync-gateway-source.yml", "branch={}".format(sync_gateway_config.sync_gateway_branch))
    else:
        print "Build stable"
        sync_gateway_base_url, sync_gateway_package_name = sync_gateway_config.sync_gateway_base_url_and_package()
        ansible_runner.run_ansible_playbook(
            "install-sync-gateway-package.yml",
            "couchbase_sync_gateway_package_base_url={0} couchbase_sync_gateway_package={1}".format(
                sync_gateway_base_url,
                sync_gateway_package_name
            )
        )

    ansible_runner.run_ansible_playbook("install-sync-gateway-service.yml", "sync_gateway_config_filepath={}".format(sync_gateway_config.sync_gateway_config_path))

if __name__ == "__main__":
    usage = """usage: python install_sync_gateway.py
    --branch=<sync_gateway_branch_to_build>
    --sync-gateway-config-file=<path_to_local_sync_gateway_config>
    """

    parser = OptionParser(usage=usage)

    parser.add_option("", "--version",
                      action="store", type="string", dest="version",
                      help="sync_gateway version to download")

    parser.add_option("", "--build-number",
                      action="store", type="string", dest="build_number",
                      help="sync_gateway build to download")

    parser.add_option("", "--sync-gateway-config-file",
                      action="store", type="string", dest="sync_gateway_config_file",
                      help="path to your sync_gateway_config file")

    parser.add_option("", "--branch",
                      action="store", type="string", dest="source_branch",
                      help="sync_gateway branch to checkout and build")

    arg_parameters = sys.argv[1:]

    (opts, args) = parser.parse_args(arg_parameters)

    sync_gateway_install_config = SyncGatewayConfig(
        version=opts.version,
        build_number=opts.build_number,
        build_from_source=opts.build_from_source,
        branch_to_build=opts.source_branch
    )

    install_sync_gateway(sync_gateway_install_config)