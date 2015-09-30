import os

from install_couchbase_server import CouchbaseServerConfig


def test_defaults():
    c = CouchbaseServerConfig()
    assert c.version == ""
    assert c.build_number == -1
    assert not c.is_valid()


def test_valid_config_3_1_0():
    # http://latestbuilds.hq.couchbase.com/couchbase-server-enterprise_centos6_x86_64_3.1.0-1805-rel.rpm
    c = CouchbaseServerConfig(
        version="3.1.0"
    )

    valid_config = c.is_valid()

    assert valid_config


def test_valid_config_3_1_1():
    # http://latestbuilds.hq.couchbase.com/couchbase-server-enterprise_centos6_x86_64_3.1.1-1807-rel.rpm
    c = CouchbaseServerConfig(
        version="3.1.1"
    )

    valid_config = c.is_valid()

    assert valid_config

    base, package = c.server_base_url_and_package()

    assert base == "http://latestbuilds.hq.couchbase.com"
    assert package == "couchbase-server-enterprise_centos6_x86_64_3.1.1-1807-rel.rpm"


def test_valid_not_config_4_0_0():
    c = CouchbaseServerConfig(
        version="4.0.0",
    )

    assert not c.is_valid()


def test_valid_config_4_0_0():

    c = CouchbaseServerConfig(
        version="4.0.0",
        build_number="4051",
    )

    assert c.is_valid()

    base, package = c.server_base_url_and_package()
    assert base == "http://latestbuilds.hq.couchbase.com/couchbase-server/sherlock/4051"
    assert package == "couchbase-server-enterprise-4.0.0-4051-centos7.x86_64.rpm"

def test_invalid_version():
    c = CouchbaseServerConfig(
        version="6.0.0",
    )

    assert not c.is_valid()