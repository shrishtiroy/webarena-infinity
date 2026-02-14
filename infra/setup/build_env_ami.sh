#!/usr/bin/env bash
# Build the Env Generator AMI (run this on a fresh Amazon Linux 2023 instance).
#
# Prerequisites: Instance with at least 8GB disk, internet access.
# After running, create an AMI from this instance.
#
# Usage:
#   bash infra/setup/build_env_ami.sh

set -euo pipefail

echo "=== Building Env Generator AMI ==="

# System packages
sudo dnf update -y
sudo dnf install -y git gcc gcc-c++ make openssl-devel bzip2-devel \
  libffi-devel zlib-devel readline-devel sqlite-devel

# Python 3.12 via uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv python install 3.12

# Node.js 20 (for Claude Code CLI and sanity checks that use Node)
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install -y nodejs

# Claude Code CLI
sudo npm install -g @anthropic-ai/claude-code

# Python dependencies for sanity checks
uv pip install --system requests python-dotenv

# Git configuration for commits
git config --global user.email "mirror-mirror-bot@example.com"
git config --global user.name "mirror-mirror-bot"

# Clone repo (will be updated on boot)
REPO_DIR="/home/ec2-user/mirror-mirror"
if [ ! -d "$REPO_DIR" ]; then
  git clone git@github.com:YOUR_ORG/mirror-mirror.git "$REPO_DIR"
fi

# Create log directory
mkdir -p /tmp/mirror-mirror-logs

echo "=== Env Generator AMI build complete ==="
echo "Next steps:"
echo "  1. Set ANTHROPIC_API_KEY and GITHUB_TOKEN in /etc/environment or user profile"
echo "  2. Create an AMI from this instance"
echo "  3. Update the repo URL above with your actual GitHub org"
