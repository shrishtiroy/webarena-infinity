#!/usr/bin/env python3
"""Agent tester worker — runs on c5.4xlarge Agent Tester instances.

Polls eval-queue for jobs, checks out the env branch, runs the parallel
evaluation against the remote env generator's servers, pushes results,
and signals completion via eval-done-queue.

Usage:
    python infra/agent_worker.py                       # run until queue empty
    python infra/agent_worker.py --once                 # process one job then exit
    python infra/agent_worker.py --workers 8            # override worker count
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    APPS_DIR,
    BRANCH_PREFIX,
    EVAL_DONE_QUEUE_URL,
    EVAL_QUEUE_URL,
    GIT_REMOTE,
    LOG_DIR,
    REPO_DIR,
    SERVERS_PER_ENV,
    SQS_VISIBILITY_TIMEOUT,
)
from sqs_utils import delete_message, receive_message, send_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [agent-worker] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

_shutdown = False


def _handle_signal(signum, frame):
    global _shutdown
    log.info("Received signal %s, finishing current job then exiting", signum)
    _shutdown = True


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git(*args: str) -> subprocess.CompletedProcess:
    cmd = ["git", *args]
    log.debug("$ %s", " ".join(cmd))
    return subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True, check=True)


def checkout_branch(branch: str) -> None:
    git("fetch", GIT_REMOTE, branch)
    git("checkout", branch)
    git("reset", "--hard", f"{GIT_REMOTE}/{branch}")


def commit_and_push(branch: str, app_dir: str, message: str) -> None:
    git("add", app_dir)
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=REPO_DIR, capture_output=True,
    )
    if result.returncode == 0:
        log.info("No result changes to commit")
        return
    git("commit", "-m", message)
    git("push", GIT_REMOTE, branch)


# ---------------------------------------------------------------------------
# Run evaluation
# ---------------------------------------------------------------------------

def run_evaluation(
    env_id: str,
    env_host: str,
    base_port: int,
    workers: int,
    model: str,
) -> dict | None:
    """Run evaluation/run_eval_parallel.py against the remote env host.

    Returns the parsed results.json or None on failure.
    """
    app_dir = os.path.join(APPS_DIR, env_id)
    eval_script = os.path.join(REPO_DIR, "evaluation", "run_eval_parallel.py")

    # Results go into the app directory so they can be committed to the branch
    output_dir = os.path.join(app_dir, "results")

    cmd = [
        sys.executable, eval_script,
        "--model", model,
        "--workers", str(workers),
        "--env-host", env_host,
        "--base-port", str(base_port),
        "--web-app", app_dir,
        "--output-dir", output_dir,
    ]

    log.info("Running eval: %s", " ".join(cmd))
    result = subprocess.run(
        cmd,
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
        timeout=3600,  # 1 hour max
    )

    if result.returncode != 0:
        log.error("Eval failed for %s:\nstdout: %s\nstderr: %s",
                  env_id, result.stdout[-500:], result.stderr[-500:])
        return None

    log.info("Eval completed for %s", env_id)

    # Find the latest results.json in the output directory
    if not os.path.isdir(output_dir):
        log.error("No output directory created for %s", env_id)
        return None

    # run_eval_parallel.py creates <model>_<timestamp>_parallel/results.json
    run_dirs = sorted(
        [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))],
        reverse=True,
    )
    if not run_dirs:
        log.error("No run directories found in %s", output_dir)
        return None

    results_path = os.path.join(output_dir, run_dirs[0], "results.json")
    if not os.path.exists(results_path):
        log.error("results.json not found at %s", results_path)
        return None

    with open(results_path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Process a single eval job
# ---------------------------------------------------------------------------

def process_eval(
    env_id: str,
    iteration: int,
    branch: str,
    env_host: str,
    base_port: int,
    workers: int,
    model: str,
) -> None:
    """Check out branch, run eval, push results, signal completion."""
    log.info("=== Eval %s iter %d (host=%s:%d) ===", env_id, iteration, env_host, base_port)

    # Step 1: Checkout the branch to get verifier code
    checkout_branch(branch)

    # Step 2: Run evaluation
    results = run_evaluation(
        env_id=env_id,
        env_host=env_host,
        base_port=base_port,
        workers=workers,
        model=model,
    )

    pass_rate = 0.0
    if results:
        pass_rate = results.get("pass_rate", 0.0)
        log.info("%s iter %d: %d/%d passed (%.1f%%)",
                 env_id, iteration,
                 results.get("passed", 0),
                 results.get("total", 0),
                 pass_rate)

    # Step 3: Commit and push results
    app_dir = os.path.join(APPS_DIR, env_id)
    commit_and_push(
        branch=branch,
        app_dir=app_dir,
        message=f"Eval results for {env_id} iteration {iteration} (pass_rate={pass_rate:.1f}%)",
    )

    # Step 4: Signal eval done
    send_message(EVAL_DONE_QUEUE_URL, {
        "env_id": env_id,
        "iteration": iteration,
        "results_branch": branch,
        "pass_rate": pass_rate,
    })
    log.info("=== Eval done for %s iter %d ===", env_id, iteration)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Agent tester worker daemon")
    parser.add_argument("--once", action="store_true", help="Process one job then exit")
    parser.add_argument("--workers", type=int, default=SERVERS_PER_ENV,
                        help="Number of parallel eval workers (default: %(default)s)")
    parser.add_argument("--model", default="gemini",
                        choices=["gpt", "gemini", "claude"],
                        help="LLM model for agents (default: %(default)s)")
    args = parser.parse_args()

    os.makedirs(LOG_DIR, exist_ok=True)

    for url_name, url_val in [
        ("EVAL_QUEUE_URL", EVAL_QUEUE_URL),
        ("EVAL_DONE_QUEUE_URL", EVAL_DONE_QUEUE_URL),
    ]:
        if not url_val:
            log.error("Missing env var: %s", url_name)
            sys.exit(1)

    log.info("Agent worker started (pid=%d, workers=%d, model=%s)",
             os.getpid(), args.workers, args.model)

    while not _shutdown:
        result = receive_message(
            EVAL_QUEUE_URL,
            visibility_timeout=SQS_VISIBILITY_TIMEOUT,
        )
        if result is None:
            if args.once:
                log.info("No message received, exiting (--once)")
                break
            continue

        body, receipt = result
        env_id = body["env_id"]
        iteration = body["iteration"]
        branch = body["branch"]
        env_host = body["env_host"]
        base_port = body.get("base_port", 8001)

        log.info("Picked up eval job: %s iter %d", env_id, iteration)

        try:
            process_eval(
                env_id=env_id,
                iteration=iteration,
                branch=branch,
                env_host=env_host,
                base_port=base_port,
                workers=args.workers,
                model=args.model,
            )
        except Exception:
            log.exception("Unhandled error evaluating %s", env_id)
            # Signal failure so env worker doesn't wait forever
            send_message(EVAL_DONE_QUEUE_URL, {
                "env_id": env_id,
                "iteration": iteration,
                "results_branch": branch,
                "pass_rate": 0.0,
                "error": "agent_worker_crash",
            })
        finally:
            delete_message(EVAL_QUEUE_URL, receipt)

        if args.once:
            break

    log.info("Agent worker exiting")


if __name__ == "__main__":
    main()
