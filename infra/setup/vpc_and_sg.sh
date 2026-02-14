#!/usr/bin/env bash
# Create VPC, subnets, security groups, NAT gateway, and SQS queues
# for the mirror-mirror scaling pipeline.
#
# Usage:
#   export AWS_REGION=us-east-1
#   bash infra/setup/vpc_and_sg.sh
#
# Outputs a sourceable env file: /tmp/mirror-mirror-infra.env

set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
TAG_KEY="Project"
TAG_VAL="mirror-mirror"
ENV_FILE="/tmp/mirror-mirror-infra.env"

echo "=== Creating VPC and networking ==="

# VPC
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=$TAG_KEY,Value=$TAG_VAL},{Key=Name,Value=mm-vpc}]" \
  --query 'Vpc.VpcId' --output text --region "$REGION")
echo "VPC: $VPC_ID"

aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-support --region "$REGION"
aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames --region "$REGION"

# Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=$TAG_KEY,Value=$TAG_VAL},{Key=Name,Value=mm-igw}]" \
  --query 'InternetGateway.InternetGatewayId' --output text --region "$REGION")
aws ec2 attach-internet-gateway --vpc-id "$VPC_ID" --internet-gateway-id "$IGW_ID" --region "$REGION"
echo "IGW: $IGW_ID"

# Public subnet (for controller)
PUB_SUBNET=$(aws ec2 create-subnet \
  --vpc-id "$VPC_ID" --cidr-block 10.0.1.0/24 --availability-zone "${REGION}a" \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=$TAG_KEY,Value=$TAG_VAL},{Key=Name,Value=mm-public}]" \
  --query 'Subnet.SubnetId' --output text --region "$REGION")
echo "Public subnet: $PUB_SUBNET"

aws ec2 modify-subnet-attribute --subnet-id "$PUB_SUBNET" --map-public-ip-on-launch --region "$REGION"

# Public route table
PUB_RT=$(aws ec2 create-route-table \
  --vpc-id "$VPC_ID" \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=$TAG_KEY,Value=$TAG_VAL},{Key=Name,Value=mm-public-rt}]" \
  --query 'RouteTable.RouteTableId' --output text --region "$REGION")
aws ec2 create-route --route-table-id "$PUB_RT" --destination-cidr-block 0.0.0.0/0 --gateway-id "$IGW_ID" --region "$REGION" > /dev/null
aws ec2 associate-route-table --subnet-id "$PUB_SUBNET" --route-table-id "$PUB_RT" --region "$REGION" > /dev/null

# Private subnet (for generators and testers)
PRIV_SUBNET=$(aws ec2 create-subnet \
  --vpc-id "$VPC_ID" --cidr-block 10.0.2.0/24 --availability-zone "${REGION}a" \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=$TAG_KEY,Value=$TAG_VAL},{Key=Name,Value=mm-private}]" \
  --query 'Subnet.SubnetId' --output text --region "$REGION")
echo "Private subnet: $PRIV_SUBNET"

# NAT Gateway (for private subnet internet access)
EIP_ALLOC=$(aws ec2 allocate-address --domain vpc \
  --tag-specifications "ResourceType=elastic-ip,Tags=[{Key=$TAG_KEY,Value=$TAG_VAL},{Key=Name,Value=mm-nat-eip}]" \
  --query 'AllocationId' --output text --region "$REGION")
NAT_GW=$(aws ec2 create-nat-gateway \
  --subnet-id "$PUB_SUBNET" --allocation-id "$EIP_ALLOC" \
  --tag-specifications "ResourceType=natgateway,Tags=[{Key=$TAG_KEY,Value=$TAG_VAL},{Key=Name,Value=mm-nat}]" \
  --query 'NatGateway.NatGatewayId' --output text --region "$REGION")
echo "NAT Gateway: $NAT_GW (waiting for available...)"
aws ec2 wait nat-gateway-available --nat-gateway-ids "$NAT_GW" --region "$REGION"

# Private route table
PRIV_RT=$(aws ec2 create-route-table \
  --vpc-id "$VPC_ID" \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=$TAG_KEY,Value=$TAG_VAL},{Key=Name,Value=mm-private-rt}]" \
  --query 'RouteTable.RouteTableId' --output text --region "$REGION")
aws ec2 create-route --route-table-id "$PRIV_RT" --destination-cidr-block 0.0.0.0/0 --nat-gateway-id "$NAT_GW" --region "$REGION" > /dev/null
aws ec2 associate-route-table --subnet-id "$PRIV_SUBNET" --route-table-id "$PRIV_RT" --region "$REGION" > /dev/null

echo "=== Creating Security Groups ==="

# Controller SG
SG_CTRL=$(aws ec2 create-security-group \
  --group-name mm-controller --description "Mirror-mirror controller" \
  --vpc-id "$VPC_ID" \
  --tag-specifications "ResourceType=security-group,Tags=[{Key=$TAG_KEY,Value=$TAG_VAL}]" \
  --query 'GroupId' --output text --region "$REGION")
# SSH from anywhere (restrict to your IP in production)
aws ec2 authorize-security-group-ingress --group-id "$SG_CTRL" --protocol tcp --port 22 --cidr 0.0.0.0/0 --region "$REGION" > /dev/null
echo "SG controller: $SG_CTRL"

# Env Generator SG
SG_ENV=$(aws ec2 create-security-group \
  --group-name mm-env-generator --description "Mirror-mirror env generators" \
  --vpc-id "$VPC_ID" \
  --tag-specifications "ResourceType=security-group,Tags=[{Key=$TAG_KEY,Value=$TAG_VAL}]" \
  --query 'GroupId' --output text --region "$REGION")
# SSH from controller SG
aws ec2 authorize-security-group-ingress --group-id "$SG_ENV" --protocol tcp --port 22 --source-group "$SG_CTRL" --region "$REGION" > /dev/null
echo "SG env generator: $SG_ENV"

# Agent Tester SG
SG_AGENT=$(aws ec2 create-security-group \
  --group-name mm-agent-tester --description "Mirror-mirror agent testers" \
  --vpc-id "$VPC_ID" \
  --tag-specifications "ResourceType=security-group,Tags=[{Key=$TAG_KEY,Value=$TAG_VAL}]" \
  --query 'GroupId' --output text --region "$REGION")
# SSH from controller SG
aws ec2 authorize-security-group-ingress --group-id "$SG_AGENT" --protocol tcp --port 22 --source-group "$SG_CTRL" --region "$REGION" > /dev/null
echo "SG agent tester: $SG_AGENT"

# Cross-SG rules: agent testers can reach env generator web servers on 8001-8008
aws ec2 authorize-security-group-ingress \
  --group-id "$SG_ENV" --protocol tcp --port 8001-8008 \
  --source-group "$SG_AGENT" --region "$REGION" > /dev/null
echo "Added rule: sg-agent → sg-env TCP 8001-8008"

echo "=== Creating SQS Queues ==="

GENERATE_Q=$(aws sqs create-queue --queue-name mirror-mirror-generate \
  --attributes '{"VisibilityTimeout":"3600","ReceiveMessageWaitTimeSeconds":"20"}' \
  --query 'QueueUrl' --output text --region "$REGION")
EVAL_Q=$(aws sqs create-queue --queue-name mirror-mirror-eval \
  --attributes '{"VisibilityTimeout":"3600","ReceiveMessageWaitTimeSeconds":"20"}' \
  --query 'QueueUrl' --output text --region "$REGION")
EVAL_DONE_Q=$(aws sqs create-queue --queue-name mirror-mirror-eval-done \
  --attributes '{"VisibilityTimeout":"60","ReceiveMessageWaitTimeSeconds":"20"}' \
  --query 'QueueUrl' --output text --region "$REGION")
PIPELINE_DONE_Q=$(aws sqs create-queue --queue-name mirror-mirror-pipeline-done \
  --attributes '{"VisibilityTimeout":"60","ReceiveMessageWaitTimeSeconds":"20"}' \
  --query 'QueueUrl' --output text --region "$REGION")

echo "Generate queue:      $GENERATE_Q"
echo "Eval queue:          $EVAL_Q"
echo "Eval-done queue:     $EVAL_DONE_Q"
echo "Pipeline-done queue: $PIPELINE_DONE_Q"

echo "=== Writing env file ==="

cat > "$ENV_FILE" <<EOF
# Generated by vpc_and_sg.sh — $(date -u +%Y-%m-%dT%H:%M:%SZ)
export AWS_REGION=$REGION
export VPC_ID=$VPC_ID
export PUB_SUBNET=$PUB_SUBNET
export PRIV_SUBNET=$PRIV_SUBNET
export SG_CTRL=$SG_CTRL
export SG_ENV=$SG_ENV
export SG_AGENT=$SG_AGENT
export NAT_GW=$NAT_GW
export GENERATE_QUEUE_URL=$GENERATE_Q
export EVAL_QUEUE_URL=$EVAL_Q
export EVAL_DONE_QUEUE_URL=$EVAL_DONE_Q
export PIPELINE_DONE_QUEUE_URL=$PIPELINE_DONE_Q
EOF

echo ""
echo "Done! Source the env file before launching instances:"
echo "  source $ENV_FILE"
