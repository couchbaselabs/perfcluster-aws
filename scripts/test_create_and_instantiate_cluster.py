import pytest
import create_and_instantiate_cluster


def test_good_config():
    c = create_and_instantiate_cluster.ClusterConfig(
        name="Test",
        server_number=5,
        server_type="xx.xxxxx",
        sync_gateway_number=10,
        sync_gateway_type="yy.yyyyyy",
        load_number=8,
        load_type="zz.zzzzzzz"
    )

    valid_config = c.is_valid()
    assert valid_config

    assert c.name == "Test"
    assert c.server_number == 5
    assert c.sync_gateway_number == 10
    assert c.load_number == 8
    assert c.server_type == "xx.xxxxx"
    assert c.sync_gateway_type == "yy.yyyyyy"
    assert c.load_type == "zz.zzzzzzz"


def test_invalid_server_type():
    c = create_and_instantiate_cluster.ClusterConfig(
        name="Test",
        server_number=5,
        server_type="xx.xxx.xx",
        sync_gateway_number=7,
        sync_gateway_type="yy.yyyyyy",
        load_number=8,
        load_type="zz.zzzzzzz"
    )

    valid_config = c.is_valid()
    assert not valid_config


def test_invalid_sg_type():
    c = create_and_instantiate_cluster.ClusterConfig(
        name="Test",
        server_number=5,
        server_type="xx.xxxxx",
        sync_gateway_number=7,
        sync_gateway_type="yy.yyyyy.y",
        load_number=8,
        load_type="zz.zzzzzzz"
    )

    valid_config = c.is_valid()
    assert not valid_config


def test_invalid_load_type():
    c = create_and_instantiate_cluster.ClusterConfig(
        name="Test",
        server_number=5,
        server_type="xx.xxxxx",
        sync_gateway_number=7,
        sync_gateway_type="yy.yyyyyy",
        load_number=8,
        load_type="zz.zz.zzzzz"
    )

    valid_config = c.is_valid()
    assert not valid_config


def test_server_limit():
    c = create_and_instantiate_cluster.ClusterConfig(
        name="Test",
        server_number=11,
        server_type="xx.xxxxx",
        sync_gateway_number=7,
        sync_gateway_type="yy.yyyyyy",
        load_number=8,
        load_type="zz.zzzzzzz"
    )

    valid_config = c.is_valid()
    assert not valid_config

def test_gateway_limit():
    c = create_and_instantiate_cluster.ClusterConfig(
        name="Test",
        server_number=9,
        server_type="xx.xxxxx",
        sync_gateway_number=11,
        sync_gateway_type="yy.yyyyyy",
        load_number=8,
        load_type="zz.zzzzzzz"
    )

    valid_config = c.is_valid()
    assert not valid_config

def test_load_limit():
    c = create_and_instantiate_cluster.ClusterConfig(
        name="Test",
        server_number=6,
        server_type="xx.xxxxx",
        sync_gateway_number=7,
        sync_gateway_type="yy.yyyyyy",
        load_number=11,
        load_type="zz.zz.zzzzz"
    )

    valid_config = c.is_valid()
    assert not valid_config



