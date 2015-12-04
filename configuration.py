NUM_CLIENTS=1
NUM_BACKUPS=1
NUM_COUCHBASE_SERVERS_DATA_CLUSTER1=2
NUM_COUCHBASE_SERVERS_DATA_CLUSTER2=0
NUM_COUCHBASE_SERVERS_DATA_CLUSTER1_NEW=0
NUM_COUCHBASE_SERVERS_DATA_CLUSTER2_NEW=0
NUM_COUCHBASE_SERVERS_INDEX=1
NUM_COUCHBASE_SERVERS_QUERY=1


CLUSTER1_NUM_SERVER_GROUPS=1

CLUSTER1_AVAILABILITY_ZONE="us-east-1a"
CLUSTER2_AVAILABILITY_ZONE="us-east-1c"

CLIENT_INSTANCE_TYPE="c3.xlarge"
COUCHBASE_INSTANCE_TYPE="r3.4xlarge" #c3.8xlarge"
BACKUP_INSTANCE_TYPE="m4.2xlarge"

CLIENT_IMAGE= "ami-xxxxxx"
COUCHBASE_IMAGE="ami-yyyyyy"
BACKUP_IMAGE="ami-zzzzz"
BACKUP_SPACE="100"
S3_BUCKET_NAME="mybucket"
