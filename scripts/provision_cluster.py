import os
import subprocess
import sys
import urlparse
import httplib
from optparse import OptionParser

# TODO Add SG package

class ProvisioningConfig:

    def __init__(self,
                 server_version,
                 build_from_source,
                 sync_gateway_branch,
                 sync_gateway_config_path,
                 server_build="",
                 sync_gateway_version="",
                 sync_gateway_build=""):

        self.__server_version = server_version
        self.__server_build = server_build
        self.__sync_gateway_version = sync_gateway_version
        self.__sync_gateway_build = sync_gateway_build

        self.__build_from_source = build_from_source
        self.__sync_gateway_branch = sync_gateway_branch
        self.__sync_gateway_config_path = os.path.abspath(sync_gateway_config_path)

    @property
    def build_from_source(self):
        return self.__build_from_source

    @property
    def sync_gateway_branch(self):
        return self.__sync_gateway_branch

    @property
    def sync_gateway_config_path(self):
        return self.__sync_gateway_config_path

    def server_base_url_and_package(self):
        return self.__base_url_package_for_server(self.__server_version, self.__server_build)

    def sync_gateway_base_url_and_package(self):
        return self.__base_url_package_for_sync_gateway(self.__sync_gateway_version, self.__sync_gateway_build)

    def __base_url_package_for_server(self, version, build):
        if version == "3.1.0":
            base_url = "http://latestbuilds.hq.couchbase.com"
            package_name = "couchbase-server-enterprise_centos6_x86_64_3.1.0-1805-rel.rpm"
            return base_url, package_name
        elif version == "3.1.1":
            base_url = "http://latestbuilds.hq.couchbase.com"
            package_name = "couchbase-server-enterprise_centos6_x86_64_3.1.1-1807-rel.rpm"
            return base_url, package_name
        elif version == "4.0.0":
            # http://latestbuilds.hq.couchbase.com/couchbase-server/sherlock/4051/couchbase-server-enterprise-4.0.0-4051-centos7.x86_64.rpm
            base_url = "http://latestbuilds.hq.couchbase.com/couchbase-server/sherlock/{0}".format(build)
            package_name = "couchbase-server-enterprise-{0}-{1}-centos7.x86_64.rpm".format(version, build)
            return base_url, package_name
        else:
            print "Server package url not found. Make sure to specify a version / build."
            sys.exit(1)

    def __base_url_package_for_sync_gateway(self, version, build):
        base_url = "http://latestbuilds.hq.couchbase.com/couchbase-sync-gateway/release/{0}/{1}-{2}".format(version, version, build)
        package_name = "couchbase-sync-gateway-enterprise_{0}-{1}_x86_64.rpm".format(version, build)
        return base_url, package_name

    def __package_exists(self, url):
        url_parts = urlparse.urlparse(url)
        host = url_parts.hostname
        path = url_parts.path
        connection = httplib.HTTPConnection(host)
        connection.request("HEAD", path)
        return connection.getresponse().status == 200

    def is_valid(self):
        if self.__build_from_source and self.__sync_gateway_branch == "":
            print "You must provide a branch to build for sync_gateway"
            return False
        if not self.__build_from_source and (self.__sync_gateway_version == "" or self.__sync_gateway_build == ""):
            print "You must provide a version and build for sync_gateway package"
            return False

        if self.__server_version == "4.0.0" and self.__server_build == "":
            print "You need to specify a build number for server version"
            return False

        if not os.path.isfile(self.__sync_gateway_config_path):
            print "Could not find sync_gateway config file: {}".format(self.__sync_gateway_config_path)
            print "Try to use an absolute path."
            return False

        return True


def provision_cluster(config):

    def run_ansible_playbook(script_name, extra_vars=""):
        if extra_vars != "":
            subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), script_name, "--extra-vars", extra_vars])
        else:
            subprocess.call(["ansible-playbook", "-l", os.path.expandvars("$KEYNAME"), script_name])

    print ">>> Provisioning cluster... "

    # Get server base url and package name
    server_base_url, server_package_name = config.server_base_url_and_package()

    print ">>> Server package: {0}/{1}".format(server_base_url, server_package_name)

    if config.build_from_source:
        print ">>> Building sync_gateway: branch={}".format(config.sync_gateway_branch)
    else:
        # TODO
        print ">>> sync_gateway package"

    print ">>> Using sync_gateway config: {}".format(config.sync_gateway_config_path)

    os.chdir("../ansible/playbooks")

    run_ansible_playbook("install-go.yml")

    # Install server package
    run_ansible_playbook(
        "install-couchbase-server-package.yml",
        "couchbase_server_package_base_url={0} couchbase_server_package_name={1}".format(server_base_url, server_package_name)
    )

   # Install sync_gateway
    if config.build_from_source:
        print "Build from source with branch: {}".format(config.sync_gateway_branch)
        run_ansible_playbook("build-sync-gateway-source.yml", "branch={}".format(config.sync_gateway_branch))
    else:
        print "Build stable"
        sync_gateway_base_url, sync_gateway_package_name = config.sync_gateway_base_url_and_package()
        run_ansible_playbook("install-sync-gateway-package.yml", "couchbase_sync_gateway_package_base_url={0} couchbase_sync_gateway_package={1}".format(
            sync_gateway_base_url,
            sync_gateway_package_name
        ))

    run_ansible_playbook("install-sync-gateway-service.yml", "sync_gateway_config_filepath={}".format(config.sync_gateway_config_path))
    run_ansible_playbook("install-splunkforwarder.yml")


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

    provisioning_config = ProvisioningConfig(
        server_version=opts.server_version,
        server_build=opts.server_build,
        sync_gateway_version=opts.sync_gateway_version,
        sync_gateway_build=opts.sync_gateway_build,
        build_from_source=opts.build_from_source,
        sync_gateway_branch=opts.source_branch,
        sync_gateway_config_path=opts.sync_gateway_config_file
    )

    if not provisioning_config.is_valid():
        print "Invalid provisioning configuration. Exiting ..."
        sys.exit(1)

    provision_cluster(provisioning_config)
