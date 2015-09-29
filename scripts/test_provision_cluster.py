import os

import provision_cluster


def test_valid_server_source():

    c = provision_cluster.ProvisioningConfig(
        server_version="3.1.0",
        build_from_source=True,
        sync_gateway_branch="master",
        sync_gateway_config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )
    assert c.is_valid()

    c = provision_cluster.ProvisioningConfig(
        server_version="3.1.1",
        build_from_source=True,
        sync_gateway_branch="master",
        sync_gateway_config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )
    assert c.is_valid()

def test_valid_config_3_1_0():

    # http://latestbuilds.hq.couchbase.com/couchbase-server-enterprise_centos6_x86_64_3.1.0-1805-rel.rpm
    c = provision_cluster.ProvisioningConfig(
        server_version="3.1.0",
        build_from_source=True,
        sync_gateway_branch="feature/distributed_index",
        sync_gateway_config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )

    valid_config = c.is_valid()

    assert valid_config
    assert c.build_from_source

    base, package = c.server_base_url_and_package()

    assert base == "http://latestbuilds.hq.couchbase.com"
    assert package == "couchbase-server-enterprise_centos6_x86_64_3.1.0-1805-rel.rpm"

    assert os.path.isfile(c.sync_gateway_config_path)
    assert c.sync_gateway_branch == "feature/distributed_index"


def test_valid_config_3_1_1():

    # http://latestbuilds.hq.couchbase.com/couchbase-server-enterprise_centos6_x86_64_3.1.1-1807-rel.rpm
    c = provision_cluster.ProvisioningConfig(
        server_version="3.1.1",
        build_from_source=True,
        sync_gateway_branch="master",
        sync_gateway_config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )

    valid_config = c.is_valid()

    assert valid_config
    assert c.build_from_source == True

    base, package = c.server_base_url_and_package()

    assert base == "http://latestbuilds.hq.couchbase.com"
    assert package == "couchbase-server-enterprise_centos6_x86_64_3.1.1-1807-rel.rpm"

    assert os.path.isfile(c.sync_gateway_config_path)
    assert c.sync_gateway_branch == "master"


def test_valid_not_config_4_0_0():
    # http://latestbuilds.hq.couchbase.com/couchbase-server/sherlock/4051/couchbase-server-community-4.0.0-4051-centos7.x86_64.rpm
    c = provision_cluster.ProvisioningConfig(
        server_version="4.0.0",
        build_from_source=True,
        sync_gateway_branch="master",
        sync_gateway_config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )

    assert not c.is_valid()


def test_valid_config_4_0_0():

    c = provision_cluster.ProvisioningConfig(
        server_version="4.0.0",
        server_build="4051",
        build_from_source=True,
        sync_gateway_branch="master",
        sync_gateway_config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )

    assert c.is_valid()

    base, package = c.server_base_url_and_package()
    assert base == "http://latestbuilds.hq.couchbase.com/couchbase-server/sherlock/4051"
    assert package == "couchbase-server-enterprise-4.0.0-4051-centos7.x86_64.rpm"


def test_in_valid_sync_gateway_config():

    c = provision_cluster.ProvisioningConfig(
        server_version="4.0.0",
        server_build="4051",
        build_from_source=True,
        sync_gateway_branch="master",
        sync_gateway_config_path="../ansible/playbooks/files/dssdfsdf"
    )

    assert not c.is_valid()


