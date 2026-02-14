#!/usr/bin/env python3
"""Environment generator worker — runs on m5.xlarge Env Generator instances.

Polls the generate-queue for jobs, runs Claude Code to generate each web app
environment, manages the sanity-check → eval → audit loop up to K iterations.

Usage:
    python infra/env_worker.py                         # default: process jobs until queue empty
    python infra/env_worker.py --once                   # process one job then exit
    python infra/env_worker.py --dry-run                # log actions without executing
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
    BASE_PORT,
    BRANCH_PREFIX,
    EVAL_DONE_QUEUE_URL,
    EVAL_QUEUE_URL,
    GENERATE_QUEUE_URL,
    GIT_REMOTE,
    LOG_DIR,
    MAX_ITERATIONS,
    PIPELINE_DONE_QUEUE_URL,
    REFERENCE_APP,
    REPO_DIR,
    SERVERS_PER_ENV,
    SQS_VISIBILITY_TIMEOUT,
)
from sqs_utils import delete_message, receive_message, send_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [env-worker] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Graceful shutdown
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

def git(*args: str, cwd: str = REPO_DIR) -> subprocess.CompletedProcess:
    cmd = ["git", *args]
    log.debug("$ %s", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)


def checkout_branch(env_id: str) -> None:
    branch = f"{BRANCH_PREFIX}{env_id.removeprefix(BRANCH_PREFIX)}"
    git("fetch", GIT_REMOTE, branch)
    git("checkout", branch)
    git("reset", "--hard", f"{GIT_REMOTE}/{branch}")


def commit_and_push(env_id: str, message: str) -> None:
    branch = f"{BRANCH_PREFIX}{env_id.removeprefix(BRANCH_PREFIX)}"
    app_dir = os.path.join(APPS_DIR, env_id)
    git("add", app_dir)
    # Check if there are staged changes
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=REPO_DIR, capture_output=True,
    )
    if result.returncode == 0:
        log.info("No changes to commit for %s", env_id)
        return
    git("commit", "-m", message)
    git("push", GIT_REMOTE, branch)


# ---------------------------------------------------------------------------
# Server management
# ---------------------------------------------------------------------------

def start_servers(app_dir: str, count: int = SERVERS_PER_ENV) -> list[subprocess.Popen]:
    """Start *count* isolated HTTP server processes on consecutive ports."""
    procs = []
    for i in range(count):
        port = BASE_PORT + i
        proc = subprocess.Popen(
            [sys.executable, "server.py", "--port", str(port)],
            cwd=app_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        procs.append(proc)
        log.info("Started server on :%d (pid %d)", port, proc.pid)
    # Wait for all servers to be ready
    import requests
    for i, proc in enumerate(procs):
        port = BASE_PORT + i
        url = f"http://localhost:{port}/"
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                r = requests.get(url, timeout=2)
                if r.status_code == 200:
                    break
            except requests.ConnectionError:
                pass
            time.sleep(0.5)
        else:
            log.warning("Server on :%d did not become ready in time", port)
    return procs


def stop_servers(procs: list[subprocess.Popen]) -> None:
    for proc in procs:
        if proc.poll() is None:
            proc.terminate()
    for proc in procs:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    log.info("All servers stopped")


# ---------------------------------------------------------------------------
# Claude Code invocation
# ---------------------------------------------------------------------------

def run_claude_code(prompt: str, app_dir: str, timeout: int = 3600) -> subprocess.CompletedProcess:
    """Invoke Claude Code CLI in non-interactive mode."""
    cmd = [
        "claude",
        "--print",          # non-interactive, stream output
        "--dangerously-skip-permissions",
        prompt,
    ]
    log.info("Running Claude Code in %s", app_dir)
    return subprocess.run(
        cmd,
        cwd=app_dir,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def generate_environment(env_id: str, docs_source: str) -> bool:
    """Use Claude Code to generate a web app environment.

    Returns True if generation succeeded (sanity check passed).
    """
    app_dir = os.path.join(APPS_DIR, env_id)
    os.makedirs(app_dir, exist_ok=True)

    # Docs are pre-seeded on the branch by seed_branches.sh (from env_manifest.jsonl).
    # No need to copy them here.

    prompt = (
        f"Generate a complete web application environment under this directory. "
        f"Use apps/{REFERENCE_APP}/ as the reference implementation — study its "
        f"server.py, index.html, js/, css/, tasks.json, tasks/*.py, and "
        f"sanity_check.py to understand the architecture. "
        f"Also follow the project-level guides at "
        f"{REPO_DIR}/docs/web-app-design-guide.md, "
        f"{REPO_DIR}/docs/task-design-guide.md, and "
        f"{REPO_DIR}/docs/environment-protocol.md. "
        f"The documentation theme for this environment is: {docs_source}. "
        f"The environment must include: server.py, index.html, js/, css/, "
        f"tasks.json (30 tasks: 10 easy, 10 medium, 10 hard), tasks/*.py verifiers, "
        f"and sanity_check.py. Make the web application a unique variation with "
        f"different seed data, UI theme, and task content from the reference. "
        f"The app must implement the state sync protocol (PUT/GET /api/state, "
        f"POST /api/reset, SSE /api/events)."
    )

    result = run_claude_code(prompt, app_dir)
    if result.returncode != 0:
        log.error("Claude Code failed for %s: %s", env_id, result.stderr[-500:])
        return False

    log.info("Claude Code generation complete for %s", env_id)
    return True


def run_sanity_check(env_id: str) -> bool:
    """Run sanity_check.py to verify all verifiers pass against solved state."""
    app_dir = os.path.join(APPS_DIR, env_id)
    sanity_script = os.path.join(app_dir, "sanity_check.py")

    if not os.path.exists(sanity_script):
        log.error("sanity_check.py not found in %s", app_dir)
        return False

    result = subprocess.run(
        [sys.executable, sanity_script, "--workers", "4"],
        cwd=app_dir,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        log.warning("Sanity check failed for %s:\n%s", env_id, result.stdout[-1000:])
        return False

    log.info("Sanity check passed for %s", env_id)
    return True


# ---------------------------------------------------------------------------
# Audit loop
# ---------------------------------------------------------------------------

def run_audit(env_id: str, iteration: int) -> bool:
    """Use Claude Code to audit evaluation results and revise if needed.

    Returns True if revisions were made (another eval needed),
    False if no changes needed (env is complete).
    """
    app_dir = os.path.join(APPS_DIR, env_id)
    results_dir = os.path.join(app_dir, "results")

    if not os.path.isdir(results_dir):
        log.warning("No results directory found for %s, skipping audit", env_id)
        return False

    # Find the latest results.json
    results_files = sorted(
        [f for f in os.listdir(results_dir) if f.endswith("results.json")],
        reverse=True,
    )
    if not results_files:
        log.warning("No results.json found for %s", env_id)
        return False

    prompt = (
        f"Audit the agent evaluation results in {results_dir}/ following the guide at "
        f"{REPO_DIR}/docs/evaluation-audit-guide.md. "
        f"This is iteration {iteration} of {MAX_ITERATIONS}. "
        f"Review each failed task and determine if the failure is due to: "
        f"(a) a verifier bug, (b) an impossible task, (c) ambiguous instructions, "
        f"(d) seed data mismatch, or (e) agent capability limitations. "
        f"For cases (a)-(d), fix the tasks/verifiers and update sanity_check.py. "
        f"For case (e), do NOT change anything. "
        f"If you made changes, respond with CHANGES_MADE. "
        f"If no changes needed, respond with NO_CHANGES."
    )

    result = run_claude_code(prompt, app_dir)
    if result.returncode != 0:
        log.error("Audit Claude Code failed for %s: %s", env_id, result.stderr[-500:])
        return False

    changes_made = "CHANGES_MADE" in result.stdout
    if changes_made:
        log.info("Audit found issues to fix for %s (iteration %d)", env_id, iteration)
        # Re-run sanity check after changes
        if not run_sanity_check(env_id):
            log.error("Sanity check failed after audit revision for %s", env_id)
            return False
        commit_and_push(env_id, f"Audit revision iteration {iteration} for {env_id}")
    else:
        log.info("Audit: no changes needed for %s", env_id)

    return changes_made


# ---------------------------------------------------------------------------
# Wait for eval-done signal
# ---------------------------------------------------------------------------

def wait_for_eval_done(env_id: str, iteration: int) -> dict | None:
    """Poll eval-done-queue for the completion signal for this env+iteration.

    Returns the message body or None on timeout.
    """
    deadline = time.time() + 7200  # 2h max wait for eval
    while time.time() < deadline:
        if _shutdown:
            return None
        result = receive_message(EVAL_DONE_QUEUE_URL, visibility_timeout=60)
        if result is None:
            continue
        body, receipt = result
        if body.get("env_id") == env_id and body.get("iteration") == iteration:
            delete_message(EVAL_DONE_QUEUE_URL, receipt)
            return body
        # Not our message — make it visible again by not deleting
        # (visibility timeout will expire and it'll reappear)
    log.error("Timed out waiting for eval-done for %s iter %d", env_id, iteration)
    return None


# ---------------------------------------------------------------------------
# Get private IP for this instance
# ---------------------------------------------------------------------------

def get_private_ip() -> str:
    """Get this instance's private IP from EC2 metadata."""
    try:
        import requests
        # IMDSv2 token
        token_resp = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=2,
        )
        token = token_resp.text
        ip_resp = requests.get(
            "http://169.254.169.254/latest/meta-data/local-ipv4",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=2,
        )
        return ip_resp.text.strip()
    except Exception:
        return "localhost"


# ---------------------------------------------------------------------------
# Process a single environment (full lifecycle)
# ---------------------------------------------------------------------------

def process_env(env_id: str, docs_source: str, start_iteration: int = 1) -> None:
    """Run the full generate → eval → audit loop for one environment."""
    log.info("=== Processing %s (source=%s, start_iter=%d) ===", env_id, docs_source, start_iteration)

    # Step 1: Checkout branch
    checkout_branch(env_id)

    # Step 2: Generate (only on first iteration)
    if start_iteration == 1:
        if not generate_environment(env_id, docs_source):
            log.error("Generation failed for %s, skipping", env_id)
            send_message(PIPELINE_DONE_QUEUE_URL, {
                "env_id": env_id,
                "final_iteration": 0,
                "pass_rate": 0,
                "status": "generation_failed",
            })
            return

        if not run_sanity_check(env_id):
            log.error("Initial sanity check failed for %s, skipping", env_id)
            send_message(PIPELINE_DONE_QUEUE_URL, {
                "env_id": env_id,
                "final_iteration": 0,
                "pass_rate": 0,
                "status": "sanity_check_failed",
            })
            return

        commit_and_push(env_id, f"Initial generation for {env_id}")

    app_dir = os.path.join(APPS_DIR, env_id)
    my_ip = get_private_ip()

    for iteration in range(start_iteration, MAX_ITERATIONS + 1):
        if _shutdown:
            log.info("Shutdown requested, stopping %s at iteration %d", env_id, iteration)
            return

        log.info("--- %s iteration %d/%d ---", env_id, iteration, MAX_ITERATIONS)

        # Step 3: Start servers
        server_procs = start_servers(app_dir)

        try:
            # Step 4: Request agent evaluation
            send_message(EVAL_QUEUE_URL, {
                "env_id": env_id,
                "iteration": iteration,
                "branch": f"{BRANCH_PREFIX}{env_id.removeprefix(BRANCH_PREFIX)}",
                "env_host": my_ip,
                "base_port": BASE_PORT,
            })
            log.info("Eval request sent for %s iter %d", env_id, iteration)

            # Step 5: Wait for eval completion
            eval_result = wait_for_eval_done(env_id, iteration)
            if eval_result is None:
                log.error("Did not receive eval-done for %s iter %d", env_id, iteration)
                break
        finally:
            # Step 6: Stop servers
            stop_servers(server_procs)

        # Step 7: Pull results committed by agent tester
        git("pull", GIT_REMOTE, f"{BRANCH_PREFIX}{env_id.removeprefix(BRANCH_PREFIX)}")

        pass_rate = eval_result.get("pass_rate", 0)
        log.info("%s iter %d: pass_rate=%.1f%%", env_id, iteration, pass_rate)

        # Step 8: Audit and possibly revise
        if iteration < MAX_ITERATIONS:
            needs_revision = run_audit(env_id, iteration)
            if not needs_revision:
                log.info("%s: audit says no changes needed, done at iter %d", env_id, iteration)
                break
            # Loop continues to next iteration with revised tasks
        else:
            # Final iteration — just audit for the record, but don't loop
            run_audit(env_id, iteration)

    # Step 9: Signal pipeline completion
    send_message(PIPELINE_DONE_QUEUE_URL, {
        "env_id": env_id,
        "final_iteration": iteration,
        "pass_rate": pass_rate,
        "status": "complete",
    })
    log.info("=== %s complete (iter=%d, pass_rate=%.1f%%) ===", env_id, iteration, pass_rate)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Env generator worker daemon")
    parser.add_argument("--once", action="store_true", help="Process one job then exit")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without executing")
    args = parser.parse_args()

    os.makedirs(LOG_DIR, exist_ok=True)

    for url_name, url_val in [
        ("GENERATE_QUEUE_URL", GENERATE_QUEUE_URL),
        ("EVAL_QUEUE_URL", EVAL_QUEUE_URL),
        ("EVAL_DONE_QUEUE_URL", EVAL_DONE_QUEUE_URL),
        ("PIPELINE_DONE_QUEUE_URL", PIPELINE_DONE_QUEUE_URL),
    ]:
        if not url_val:
            log.error("Missing env var: %s", url_name)
            sys.exit(1)

    log.info("Env worker started (pid=%d)", os.getpid())

    while not _shutdown:
        result = receive_message(
            GENERATE_QUEUE_URL,
            visibility_timeout=SQS_VISIBILITY_TIMEOUT,
        )
        if result is None:
            if args.once:
                log.info("No message received, exiting (--once)")
                break
            continue

        body, receipt = result
        env_id = body["env_id"]
        docs_source = body["docs_source"]
        start_iteration = body.get("iteration", 1)

        log.info("Picked up job: %s (source=%s)", env_id, docs_source)

        try:
            if not args.dry_run:
                process_env(env_id, docs_source, start_iteration)
            else:
                log.info("[dry-run] Would process %s", env_id)
        except Exception:
            log.exception("Unhandled error processing %s", env_id)
        finally:
            delete_message(GENERATE_QUEUE_URL, receipt)

        if args.once:
            break

    log.info("Env worker exiting")


if __name__ == "__main__":
    main()
