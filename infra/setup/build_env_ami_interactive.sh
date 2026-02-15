#!/usr/bin/env bash
# Launch a temporary env generator instance, SSH in to do `claude login`,
# then create a reusable AMI with the session baked in.
#
# This is a ONE-TIME setup step. The resulting AMI is used by launch_pipeline.sh.
#
# Prerequisites:
#   source /tmp/mirror-mirror-infra.env
#   export KEY_PAIR_NAME=... GITHUB_TOKEN=...
#
# Usage:
#   bash infra/setup/build_env_ami_interactive.sh
#
# What happens:
#   1. Launches an m5.xlarge in the PUBLIC subnet (so you can SSH)
#   2. Installs all env generator deps via user-data
#   3. Waits for setup, then tells you to SSH in and run `claude login`
#   4. After you confirm login is done, creates an AMI
#   5. Terminates the build instance
#   6. Saves the AMI ID to /tmp/mirror-mirror-infra.env

set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"

for var in PUB_SUBNET SG_CTRL KEY_PAIR_NAME GITHUB_TOKEN; do
  if [ -z "${!var:-}" ]; then
    echo "ERROR: $var is not set"
    exit 1
  fi
done

# --- Find base AMI ---
AL2023_AMI=$(aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023*-x86_64" "Name=state,Values=available" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text --region "$REGION")
echo "Base AMI: $AL2023_AMI"

# --- User-data: install everything ---
USERDATA=$(cat <<'SETUP_EOF'
#!/bin/bash
set -euo pipefail
exec > /var/log/mirror-mirror-setup.log 2>&1

export HOME=/home/ec2-user
cd $HOME

# System packages
dnf update -y
dnf install -y git gcc gcc-c++ make openssl-devel bzip2-devel \
  libffi-devel zlib-devel readline-devel sqlite-devel

# Python via uv
su - ec2-user -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
su - ec2-user -c 'export PATH="$HOME/.local/bin:$PATH" && uv python install 3.12'

# Create a venv and install deps via uv
su - ec2-user -c 'export PATH="$HOME/.local/bin:$PATH" && uv venv $HOME/venv --python 3.12'
su - ec2-user -c 'export PATH="$HOME/.local/bin:$PATH" && VIRTUAL_ENV=$HOME/venv uv pip install requests python-dotenv boto3'

# Add venv to PATH in bashrc so workers use it
echo 'export PATH="$HOME/venv/bin:$HOME/.local/bin:$PATH"' >> /home/ec2-user/.bashrc

# Node.js 20
curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
dnf install -y nodejs

# Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Git config
su - ec2-user -c 'git config --global user.email "mirror-mirror-bot@example.com"'
su - ec2-user -c 'git config --global user.name "mirror-mirror-bot"'

# Create log dir
mkdir -p /tmp/mirror-mirror-logs

# Signal that setup is done
touch /home/ec2-user/.setup-complete
echo "Setup complete!"
SETUP_EOF
)

# --- IAM role ---
ROLE_NAME="mirror-mirror-ec2"
if ! aws iam get-role --role-name "$ROLE_NAME" 2>/dev/null; then
  echo "Creating IAM role: $ROLE_NAME"
  aws iam create-role --role-name "$ROLE_NAME" \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]
    }' > /dev/null
  aws iam attach-role-policy --role-name "$ROLE_NAME" \
    --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess
  aws iam create-instance-profile --instance-profile-name "$ROLE_NAME" > /dev/null
  aws iam add-role-to-instance-profile --instance-profile-name "$ROLE_NAME" --role-name "$ROLE_NAME"
  sleep 10
fi

# --- Launch build instance ---
echo ""
echo "=== Launching build instance ==="
BUILD_ID=$(aws ec2 run-instances \
  --image-id "$AL2023_AMI" \
  --instance-type m5.xlarge \
  --key-name "$KEY_PAIR_NAME" \
  --subnet-id "$PUB_SUBNET" \
  --security-group-ids "$SG_CTRL" \
  --iam-instance-profile Name="$ROLE_NAME" \
  --user-data "$(echo "$USERDATA" | base64)" \
  --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":30}}]' \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=mm-ami-build},{Key=Project,Value=mirror-mirror}]" \
  --query 'Instances[0].InstanceId' --output text --region "$REGION")
echo "  Instance: $BUILD_ID"

echo "  Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids "$BUILD_ID" --region "$REGION"

PUBLIC_IP=$(aws ec2 describe-instances --instance-ids "$BUILD_ID" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text --region "$REGION")
echo "  Public IP: $PUBLIC_IP"

echo ""
echo "=== Waiting for setup to complete (~5 min) ==="
echo "  You can watch progress with:"
echo "    ssh -i ~/.ssh/${KEY_PAIR_NAME}.pem ec2-user@${PUBLIC_IP} 'tail -f /var/log/mirror-mirror-setup.log'"
echo ""

# Poll for setup completion
for i in $(seq 1 60); do
  if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
    -i "$HOME/.ssh/${KEY_PAIR_NAME}.pem" "ec2-user@${PUBLIC_IP}" \
    'test -f ~/.setup-complete' 2>/dev/null; then
    echo "  Setup complete!"
    break
  fi
  sleep 10
  printf "  waiting... (%d/60)\n" "$i"
done

echo ""
echo "============================================================"
echo "  Now SSH in and run 'claude login':"
echo ""
echo "    ssh -i ~/.ssh/${KEY_PAIR_NAME}.pem ec2-user@${PUBLIC_IP}"
echo ""
echo "  Once inside:"
echo "    claude login"
echo ""
echo "  Follow the browser prompts to authenticate with your Max plan."
echo "  After login succeeds, type 'exit' to return here."
echo "============================================================"
echo ""
read -p "Press ENTER after you've completed 'claude login' on the instance... "

# --- Clone repo (needs to happen after GITHUB_TOKEN is available) ---
echo "Cloning repo on instance..."
ssh -o StrictHostKeyChecking=no -i "$HOME/.ssh/${KEY_PAIR_NAME}.pem" "ec2-user@${PUBLIC_IP}" \
  "git clone https://${GITHUB_TOKEN}@github.com/shuyanzhou/mirror-mirror.git /home/ec2-user/mirror-mirror 2>/dev/null || (cd /home/ec2-user/mirror-mirror && git pull)"

# --- Create AMI ---
echo ""
echo "=== Creating AMI (this takes 3-5 min) ==="
AMI_ID=$(aws ec2 create-image \
  --instance-id "$BUILD_ID" \
  --name "mm-env-generator-$(date +%Y%m%d-%H%M%S)" \
  --description "Mirror-mirror env generator with Claude Code logged in" \
  --tag-specifications "ResourceType=image,Tags=[{Key=Project,Value=mirror-mirror},{Key=Role,Value=env-generator}]" \
  --query 'ImageId' --output text --region "$REGION")
echo "  AMI: $AMI_ID"

echo "  Waiting for AMI to be available..."
aws ec2 wait image-available --image-ids "$AMI_ID" --region "$REGION"
echo "  AMI ready!"

# --- Terminate build instance ---
echo "  Terminating build instance..."
aws ec2 terminate-instances --instance-ids "$BUILD_ID" --region "$REGION" > /dev/null

# --- Save AMI ID ---
echo "export ENV_AMI_ID=$AMI_ID" >> /tmp/mirror-mirror-infra.env
echo ""
echo "=== Done ==="
echo "  ENV_AMI_ID=$AMI_ID saved to /tmp/mirror-mirror-infra.env"
echo "  Use this AMI for all env generators — Claude session is baked in."
echo ""
echo "  Next: source /tmp/mirror-mirror-infra.env && bash infra/setup/launch_pipeline.sh 5"
