import os

from install_sync_gateway import SyncGatewayConfig


def test_missing_build_number():
    c = SyncGatewayConfig(
        version="1.1.0",
        build_number=None,
        branch=None,
        config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )
    assert not c.is_valid()


def test_missing_version_with_build():
    c = SyncGatewayConfig(
        version=None,
        build_number=21,
        branch=None,
        config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )
    assert not c.is_valid()


def test_build_from_source():
    c = SyncGatewayConfig(
        branch="master",
        build_number=None,
        version=None,
        config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )
    assert c.is_valid()


def test_invalid_config_1():
    c = SyncGatewayConfig(
        version="1.0.0",
        branch="master",
        build_number=None,
        config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )
    assert not c.is_valid()


def test_invalid_config_2():
    c = SyncGatewayConfig(
        build_number=21,
        branch="master",
        version=None,
        config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )
    assert not c.is_valid()


def test_sync_gateway_config():
    c = SyncGatewayConfig(
        version=None,
        build_number=None,
        branch="master",
        config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )
    assert c.is_valid()


def test_invalid_sync_gateway_config():
    c = SyncGatewayConfig(
        version=None,
        build_number=None,
        branch="master",
        config_path="../ansible/playbooks/files/sync_gateway_config.j"
    )
    assert not c.is_valid()


def test_1_1_0():
    # http://latestbuilds.hq.couchbase.com/couchbase-sync-gateway/release/1.1.0/1.1.0-21/couchbase-sync-gateway-enterprise_1.1.0-21_x86_64.rpm
    c = SyncGatewayConfig(
        version="1.1.0",
        build_number=21,
        branch=None,
        config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )

    u, p = c.sync_gateway_base_url_and_package()

    assert u == "http://latestbuilds.hq.couchbase.com/couchbase-sync-gateway/release/1.1.0/1.1.0-21"
    assert p == "couchbase-sync-gateway-enterprise_1.1.0-21_x86_64.rpm"
    assert c.is_valid()


def test_1_1_1():
    # http://latestbuilds.hq.couchbase.com/couchbase-sync-gateway/release/1.1.1/1.1.1-10/couchbase-sync-gateway-enterprise_1.1.1-10_x86_64.rpm
    c = SyncGatewayConfig(
        version="1.1.1",
        build_number=10,
        branch=None,
        config_path="../ansible/playbooks/files/sync_gateway_config.json"
    )

    u, p = c.sync_gateway_base_url_and_package()

    assert u == "http://latestbuilds.hq.couchbase.com/couchbase-sync-gateway/release/1.1.1/1.1.1-10"
    assert p == "couchbase-sync-gateway-enterprise_1.1.1-10_x86_64.rpm"
    assert c.is_valid()


