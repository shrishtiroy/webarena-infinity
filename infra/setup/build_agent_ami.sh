#!/usr/bin/env bash
# Build the Agent Tester AMI (run this on a fresh Amazon Linux 2023 instance).
#
# Prerequisites: Instance with at least 20GB disk (Chromium is ~400MB), internet access.
# After running, create an AMI from this instance.
#
# Usage:
#   bash infra/setup/build_agent_ami.sh

set -euo pipefail

echo "=== Building Agent Tester AMI ==="

# System packages (including Chromium dependencies)
sudo dnf update -y
sudo dnf install -y git gcc gcc-c++ make openssl-devel bzip2-devel \
  libffi-devel zlib-devel readline-devel sqlite-devel \
  alsa-lib atk at-spi2-atk cups-libs libdrm mesa-libgbm \
  pango libXcomposite libXdamage libXrandr libxkbcommon \
  nss nspr

# Python 3.12 via uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv python install 3.12

# Node.js 20 (may be needed for some verifiers)
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install -y nodejs

# Python dependencies
uv pip install --system \
  "browser-use>=0.11.9" \
  requests \
  python-dotenv \
  boto3

# Install Playwright + Chromium
uv run playwright install chromium
uv run playwright install-deps

# Git configuration
git config --global user.email "mirror-mirror-bot@example.com"
git config --global user.name "mirror-mirror-bot"

# Clone repo
REPO_DIR="/home/ec2-user/mirror-mirror"
if [ ! -d "$REPO_DIR" ]; then
  git clone git@github.com:YOUR_ORG/mirror-mirror.git "$REPO_DIR"
fi

# Create log directory
mkdir -p /tmp/mirror-mirror-logs

echo "=== Agent Tester AMI build complete ==="
echo "Next steps:"
echo "  1. Set OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY, GITHUB_TOKEN"
echo "  2. Create an AMI from this instance"
echo "  3. Update the repo URL above with your actual GitHub org"
