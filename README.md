
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

## Install steps (Simplified Version)

### Creates topology and starts the Cloudformation stack on AWS

```
python scripts/create_and_instantiate_cluster.py 
    --stackname="YourCloudFormationStack"
    --num-servers=2
    --num-sync-gateways=1
    --num-gatlings=1
```

This script performs a series of steps for you
1) It uses [troposphere](https://github.com/cloudtools/troposphere) to generate the Cloudformation template (a json file). The Cloudformation config is declared via a Python DSL, which then generates the Cloudformation Json.
2) The generated template is uploaded to AWS with ssh access to the AWS_KEY name you specified (assuming that you have set up that keypair in AWS prior to this)

### Provision the cluster

Install Couchbase Server and build sync_gateway from source with optional --branch (master is default)

```
python scripts/provision_cluster.py 
    --server-version=3.1.0
    --build-from-source
    --branch="feature/distributed_cache_stale_ok"
```

(IN PROGRESS) Install Couchbase Server and download sync_gateway binary (1.1.1 is default)

```
python scripts/provision_cluster.py 
    --server-version=3.1.0
    --sync-gateway-version=1.1.1
```

### Setup and run gatling tests

```
python scripts/run_tests.py
    --number-pullers=0
    --number-pushers=7500
```

### Teardown cluster

```
 python scripts/teardown_cluster.py 
    --stackname="YourCloudFormationStack"
```

## More control
### If you require debugging specific scipts or need more control, you are still able to do many of the steps one by one

### Kick off EC2 instances

**Via AWS CLI**

```
aws cloudformation create-stack --stack-name CouchbasePerfCluster --region us-east-1 \
--template-body "file://cloudformation_template.json" \
--parameters "ParameterKey=KeyName,ParameterValue=<your_keypair_name>"
```

Alternatively, it can be kicked off via the AWS web UI with the restriction that the AWS cloudformation_template.json file must be uploaded to [S3](http://couchbase-mobile.s3.amazonaws.com/perfcluster-aws/cloudformation_template.json).

### Provision EC2 instances

* `cd ansible/playbooks`
* Run command
```
ansible-playbook -l $KEYNAME install-go.yml && \
ansible-playbook -l $KEYNAME install-couchbase-server-3.1.0.yml && \
ansible-playbook -l $KEYNAME build-sync-gateway.yml && \
ansible-playbook -l $KEYNAME build-gateload.yml && \
ansible-playbook -l $KEYNAME install-sync-gateway-service.yml && \
ansible-playbook -l $KEYNAME install-splunkforwarder.yml
```

To use a different Sync Gateway branch:

Replace:

```
ansible-playbook -l $KEYNAME build-sync-gateway.yml
```

with:

```
ansible-playbook -l $KEYNAME build-sync-gateway.yml --extra-vars "branch=feature/distributed_cache_stale_ok"
```

If you are testing the Sync Gateway distributed cache branch, one extra step is needed:

```
ansible-playbook -l $KEYNAME configure-sync-gateway-writer.yml
```

### Starting Gateload tests

```
$ cd ../..
$ python generate_gateload_configs.py  # generates and uploads gateload configs with correct SG IP / user offset
$ cd ansible/playbooks
$ ansible-playbook -l $KEYNAME start-gateload.yml
```

### Starting Gatling tests

```
$ ansible-playbook -l $KEYNAME configure-gatling.yml
$ ansible-playbook -l $KEYNAME run-gatling-theme.yml
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
