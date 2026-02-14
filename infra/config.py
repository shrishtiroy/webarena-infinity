"""Shared configuration for the AWS scaling pipeline.

All settings come from environment variables with sensible defaults.
Import this module from orchestrator, env_worker, and agent_worker.
"""

import os

# ---------------------------------------------------------------------------
# AWS Region
# ---------------------------------------------------------------------------
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# ---------------------------------------------------------------------------
# SQS Queue URLs (set after creating queues via setup/vpc_and_sg.sh)
# ---------------------------------------------------------------------------
GENERATE_QUEUE_URL = os.environ.get("GENERATE_QUEUE_URL", "")
EVAL_QUEUE_URL = os.environ.get("EVAL_QUEUE_URL", "")
EVAL_DONE_QUEUE_URL = os.environ.get("EVAL_DONE_QUEUE_URL", "")
PIPELINE_DONE_QUEUE_URL = os.environ.get("PIPELINE_DONE_QUEUE_URL", "")

# ---------------------------------------------------------------------------
# Pipeline parameters
# ---------------------------------------------------------------------------
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "3"))  # K=3 audit loops
TOTAL_ENVS = int(os.environ.get("TOTAL_ENVS", "100"))
ENVS_PER_GENERATOR = int(os.environ.get("ENVS_PER_GENERATOR", "10"))

# ---------------------------------------------------------------------------
# Server configuration
# ---------------------------------------------------------------------------
SERVERS_PER_ENV = 8          # one server per eval worker (mutable state isolation)
BASE_PORT = 8001             # first server port
MAX_PORT = BASE_PORT + SERVERS_PER_ENV - 1  # 8008

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_DIR = os.environ.get("REPO_DIR", "/home/ec2-user/mirror-mirror")
APPS_DIR = os.path.join(REPO_DIR, "apps")
REFERENCE_APP = "gitlab-org-management"  # the example app visible on every branch

# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------
GIT_REMOTE = "origin"
BRANCH_PREFIX = "env-"

# ---------------------------------------------------------------------------
# SQS polling
# ---------------------------------------------------------------------------
SQS_WAIT_TIME = 20            # long-poll seconds (max 20)
SQS_VISIBILITY_TIMEOUT = 3600 # 1 hour — enough for generation + sanity check

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_DIR = os.environ.get("LOG_DIR", "/tmp/mirror-mirror-logs")
