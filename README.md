
Automation to setup a performance test cluster on AWS with:

* Couchbase Server nodes
* Sync Gateway nodes
* Gateload and/or Gatling nodes

Uses a Cloudformation template to spin up all instances.

## Install pre-requisites

**Python Dependencies**

```
$ pip install ansible
$ pip install boto
$ pip install troposphere
$ pip install awscli
```

Alternatively, you can use the [Docker image](https://github.com/couchbaselabs/perfcluster-aws/wiki/Running-under-Docker) which has all the pre-requisites pre-installed.

**Add boto configuration**

```
$ cat >> ~/.boto
[Credentials]
aws_access_key_id = CDABGHEFCDABGHEFCDAB
aws_secret_access_key = ABGHEFCDABGHEFCDABGHEFCDABGHEFCDABGHEFCDAB
^D
```

(and replace fake credentials above with your real credentials)

**Add AWS env variables**

```
$ export AWS_ACCESS_KEY_ID=CDABGHEFCDABGHEFCDAB
$ export AWS_SECRET_ACCESS_KEY=ABGHEFCDABGHEFCDABGHEFCDABGHEFCDABGHEFCDAB
$ export AWS_KEY=<your-aws-keypair-name>
```

**To run tests or ansible scripts**

```
$ export KEYNAME=key_<your-aws-keypair-name>
```

**To gather data in Splunk you will want to set variable below

```
$ export SPLUNK_SERVER="<url_of_splunk_server>:<port>"
$ export SPLUNK_SERVER_AUTH="<username>:<password>"
```

## Install steps 

`cd scripts` to get into the scripts subdirectory.

### Creates topology and starts the Cloudformation stack on AWS

```
python create_and_instantiate_cluster.py 
    --stackname="YourCloudFormationStack"
    --num-servers=2
    --server-type="m3.large"
    --num-sync-gateways=1
    --sync-gateway-type="m3.medium"
    --num-gatlings=1
    --gatling-type="m3.medium"
```

This script performs a series of steps for you

1) It uses [troposphere](https://github.com/cloudtools/troposphere) to generate the Cloudformation template (a json file). The Cloudformation config is declared via a Python DSL, which then generates the Cloudformation Json.

2) The generated template is uploaded to AWS with ssh access to the AWS_KEY name you specified (assuming that you have set up that keypair in AWS prior to this)

### Provision the cluster

Install Couchbase Server and build sync_gateway from source with optional --branch (master is default).
Additionally, you can provide an optional custom sync_gateway_config.json file. If this is not specified, it will use the config in "perfcluster-aws/ansible/playbooks/files/sync_gateway_config.json"

```
python provision_cluster.py 
    --server-version=3.1.0
    --sync-gateway-branch="feature/distributed_cache_stale_ok"
    --sync-gateway-config-file="<absolute path to your sync_gateway_config.json file>" (optional)
```

(IN PROGRESS) Install Couchbase Server and download sync_gateway binary (1.1.1 is default)

```
python provision_cluster.py 
    --server-version=3.1.0
    --sync-gateway-version=1.1.1
    --sync-gateway-build=10
```

### Install Couchbase Server

Will install Couchbase Server in the cluster on all couchbase server nodes

```
python install_couchbase_server.py
    --version=<couchbase_server_version>
    --build-number=<server_build_number>
```

### Install sync_gateway

Will install sync_gateway in the cluster on all sync_gateway nodes. Uses perfcluster-aws/ansible/playbooks/files/sync_gateway_config.json by default

From source

```
python install_sync_gateway.py
    --branch=<sync_gateway_branch_to_build>
    --config-file-path=<path_to_local_sync_gateway_config> (optional)
```

or from release (IN PROGRESS)

```
python install_sync_gateway.py
    --version=<couchbase_server_version>
    --build-number=<server_build_number>
    --config-file-path=<path_to_local_sync_gateway_config> (optional)
```

### Setup and run gatling tests

```
python run_tests.py
    --number-pullers=0
    --number-pushers=7500
```

### Setup and run gateload tests

Currently the load generation is specified in ansible/files/gateload_config.json.
(In progress) Allow this to be parameterized

```
python run_tests.py
    --use-gateload
```

### Restart sync_gateway

The following command will execute a few steps

1) Flush bucket-1 and bucket-2 in Couchbase Server

2) Stop running sync_gateway services

3) Remove sync_gateway logs

4) Restart sync_gateway services

```
python reset_sync_gateway.py
```

### Kill gateload

The following command will kill running gateload processes

```
python kill_gateload.py
```

### Teardown cluster

```
 python teardown_cluster.py 
    --stackname="YourCloudFormationStack"
```

### Distributed index branch testing note

If you are testing the Sync Gateway distributed index branch, one extra step is needed:

```
ansible-playbook -l $KEYNAME configure-sync-gateway-writer.yml
```

### Starting Gateload tests

If you need to run Gateload rather than Gatling, do the following steps

```
$ cd ../..
$ python generate_gateload_configs.py  # generates and uploads gateload configs with correct SG IP / user offset
$ cd ansible/playbooks
$ ansible-playbook -l $KEYNAME start-gateload.yml
```

### View Gatelod test output

* Sync Gateway expvars on $HOST:4985/_expvar

* Gateload expvars $HOST:9876/debug/var

* Gateload expvar snapshots

    * ssh into gateload, and `ls expvar*` to see snapshots

    * ssh into gateload, and run `screen -r gateload` to view gateload logs

## Viewing instances by type

To view all couchbase servers:

```
$ ansible tag_Type_couchbaseserver --list-hosts
```

The same can be done for Sync Gateways and Gateload instances.  Here are the full list of tag filters:

* tag_Type_couchbaseserver
* tag_Type_syncgateway
* tag_Type_gateload

## Collecting expvar output

```
while [ 1 ]
do
    outfile=$(date +%s)
    curl localhost:9876/debug/vars -o ${outfile}.json
    echo "Saved output to $outfile"
    sleep 60
done
```

## Viewing data on Splunk

First, you will need to [Install Splunk](https://github.com/couchbaselabs/perfcluster-aws/wiki/Setting-up-a-Splunk-Server) on a server somewhere.

Note: The data collected by the unix app is by default placed into a separate index called ‘os’ so it will not be searchable within splunk unless you either go through the UNIX app, or include the following in your search query: “index=os” or “index=os OR index=main” (don’t paste doublequotes)
