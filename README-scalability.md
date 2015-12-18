
Automation to setup a performance test cluster on AWS with:

* Couchbase Server nodes

Uses a Cloudformation template to spin up all instances.

## Install pre-requisites
```
$ sudo apt-get update 
$ sudo apt-get install python-pip
$ sudo apt-get install python-dev
$ sudo apt-get install git

$ git clone https://github.com/owendCB/perfcluster-aws.git
```
**Python Dependencies**

```
$ sudo pip install ansible
$ sudo pip install boto
$ sudo pip install troposphere
$ sudo pip install awscli
$ sudo pip install markupsafe
```

**Add boto configuration**

```
$ cat >> ~/.boto
[Credentials]
aws_access_key_id = CDABGHEFCDABGHEFCDAB
aws_secret_access_key = ABGHEFCDABGHEFCDABGHEFCDABGHEFCDABGHEFCDAB
^D
```
(and replace fake credentials above with your real credentials)
### Important Security Note:
Given this instance will contain your aws_access_key_id, aws_secret_access_key
and <your_keypair_name>.pem file, it is very important that you keep it secure by
using a securitygroup with only limited access.  Provding ssh access (port 22) from
your desktop machine should be all that is required.


**Add <your_keypair_name>.pem authentication**

```
$ scp -i <your_keypair_name>.pem <your_keypair_name>.pem ubuntu@11.22.33.44:/home/ubuntu
$ ssh -i <your_keypair_name>.pem ubuntu@11.22.33.44
$ ssh-agent bash
$ ssh-add <your_keypair_name>.pem
```

**Add AWS env variables**

```
$ export AWS_ACCESS_KEY_ID=CDABGHEFCDABGHEFCDAB
$ export AWS_SECRET_ACCESS_KEY=ABGHEFCDABGHEFCDABGHEFCDABGHEFCDABGHEFCDAB
```

## How to generate CloudFormation template

This uses [troposphere](https://github.com/cloudtools/troposphere) to generate the Cloudformation template (a json file).

The Cloudformation config is declared via a Python DSL, which then generates the Cloudformation Json.

### Modify the configurion file
```
NUM_CLIENTS=1
NUM_BACKUPS=1
NUM_COUCHBASE_SERVERS_DATA_CLUSTER1=2
NUM_COUCHBASE_SERVERS_DATA_CLUSTER2=0
NUM_COUCHBASE_SERVERS_DATA_CLUSTER1_NEW=0
NUM_COUCHBASE_SERVERS_DATA_CLUSTER2_NEW=0
NUM_COUCHBASE_SERVERS_INDEX=1
NUM_COUCHBASE_SERVERS_QUERY=1

# minimum of 1, maximum of 4
CLUSTER1_NUM_SERVER_GROUPS=1

CLUSTER1_AVAILABILITY_ZONE="us-east-1a"
CLUSTER2_AVAILABILITY_ZONE="us-east-1c"

CLIENT_INSTANCE_TYPE="c3.xlarge"
COUCHBASE_INSTANCE_TYPE="r3.4xlarge"
BACKUP_INSTANCE_TYPE="r3.4xlarge"

CLIENT_IMAGE= "ami-xxxxxx"
COUCHBASE_IMAGE="ami-yyyyyy"
BACKUP_IMAGE="ami-zzzzz"
BACKUP_SPACE="100"
S3_BUCKET_NAME="mybucket"

```
The COUCHBASE_IMAGE needs to contain an installation of couchbase, that has not been configured.
The configuration file will be used when genration the Cloudformation template files.  See ./update.sh script below.

## Upload to S3

Because of the size of the templates they need to be uploaded to S3 before they can be run.

### Creating the bucket
Login to AWS.  Go to S3 and select create bucket.  Select US standard as the Region.  Use the unique bucket name you specified in the configuration.py file.  The same bucket name is also used in the export below.

```
$ export S3_BUCKET_NAME=mybucket
```

## Generate the templates and upload the files to S3 bucket
The following script will do all the necessary work for you.  Just make sure you have exported AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and S3_BUCKET_NAME.

```
./update.sh
```

## Install steps

### Kick off EC2 instances

**Via AWS CLI**

Note the template-url contains the bucket name (which is cb-scalability in the example below).
So you will need to change this to your bucket name

```
aws cloudformation create-stack --stack-name ScalabilityPerfCluster --region us-east-1 --template-url https://cb-scalability.s3.amazonaws.com/scalability_top.json --parameters "ParameterKey=KeyName,ParameterValue=<your_keypair_name>"
```

Note: CloudFormation is a top-level AWS service (i.e. like EC2 and VPC).  If you click on the CloudFormation service you should see the stack ScalabilityPerfCluster

### Provision EC2 instances

```
cd ansible/playbooks
export KEYNAME=key_<your_keypair_name>  ***Note the "key_" before <your_keypair_name>
ansible-playbook -l $KEYNAME scalability-configure-test1-1-bucket-heterogeneous-couchbase.yml
```

### Running test on configured instance
```
cd ansible/playbooks
export KEYNAME=key_<your_keyname_name>
ansible-playbook -l $KEYNAME scalability-test1-1bucket.yml
```

## Viewing instances by type

To view all couchbase servers:

```
$ ansible tag_Type_couchbaseserver --list-hosts
```

## The Tests

Scripts exist to test with a single bucket and ten buckets.

The configure file does not need to be changed for different number of buckets.

### Test 1 (Usability) & Test 2 (Linear Scalability)

For test 2 vary the NUM_COUCHBASE_SERVERS_DATA_CLUSTER1 parameter to 32 and 64

```
NUM_CLIENTS=64
NUM_BACKUPS=0
NUM_COUCHBASE_SERVERS_DATA_CLUSTER1=128
NUM_COUCHBASE_SERVERS_DATA_CLUSTER2=0
NUM_COUCHBASE_SERVERS_DATA_CLUSTER1_NEW=0
NUM_COUCHBASE_SERVERS_DATA_CLUSTER2_NEW=0
NUM_COUCHBASE_SERVERS_INDEX=1
NUM_COUCHBASE_SERVERS_QUERY=1

# minimum of 1, maximum of 4
CLUSTER1_NUM_SERVER_GROUPS=4

CLUSTER1_AVAILABILITY_ZONE="us-east-1a"
CLUSTER2_AVAILABILITY_ZONE="us-east-1c"

CLIENT_INSTANCE_TYPE="c3.xlarge"
COUCHBASE_INSTANCE_TYPE="r3.4xlarge"
BACKUP_INSTANCE_TYPE="r3.4xlarge"

CLIENT_IMAGE= "ami-xxxxxx"
COUCHBASE_IMAGE="ami-yyyyyy"
BACKUP_IMAGE="ami-zzzzz"
BACKUP_SPACE="100"
S3_BUCKET_NAME="mybucket"

./update.sh
cd ansible/playbooks

ansible-playbook -l $KEYNAME tests/test1-1bucket-configure.yml
ansible-playbook -l $KEYNAME tests/test1-1bucket-run.yml

```

### Test 3 (Infrequent Analytical View Performance)

Same configuration parameters as used in Test 1 and 2

```
ansible-playbook -l $KEYNAME tests/test3-1bucket-configure.yml
ansible-playbook -l $KEYNAME tests/test3-1bucket-run.yml
```

### Test 4 (Fail-over Performance)

Same set-up as Test 1.

I manually select graceful failover of a single data node.

### Test 5 (Rebalance Performance - Node Failure Use Case)

Follow-on from Test 4 to select full-recovery of the node that was failed over, and then do a rebalance

Again I manually perform this test.

### Test 6 (Rebalance Performance - Capacity Growth Use Case)

Same configuration parameters as used in Test 1 and 2.

Note the initial run file is also the same as used in Test 1 (only the configuration file is different.)

```
ansible-playbook -l $KEYNAME tests/test6-1bucket-configure.yml
ansible-playbook -l $KEYNAME tests/test1-1bucket-run.yml
```

Once fully populated with 64M data items we add the extra nodes and rebalance them in.
All the new nodes will be added into server group: 'Group 4'.

```
ansible-playbook -l $KEYNAME tests/test6-run.yml
```
