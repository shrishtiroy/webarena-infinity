#!/usr/bin/env python3
"""Controller orchestrator — runs on the t3.medium controller instance.

Responsibilities:
  1. Read infra/env_manifest.jsonl to know which envs to generate.
  2. Seed the generate-queue with one job per manifest entry.
  3. Monitor pipeline-done-queue for completion signals.
  4. Print live progress and exit when all envs are done.

Usage:
    python infra/orchestrator.py                                    # seed + monitor
    python infra/orchestrator.py --manifest infra/env_manifest.jsonl
    python infra/orchestrator.py --monitor-only --total-envs 5      # skip seeding
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    GENERATE_QUEUE_URL,
    PIPELINE_DONE_QUEUE_URL,
    REPO_DIR,
)
from sqs_utils import delete_message, receive_message, send_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [orchestrator] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

DEFAULT_MANIFEST = os.path.join(REPO_DIR, "infra", "env_manifest.jsonl")


def load_manifest(path: str) -> list[dict]:
    """Read the JSONL manifest.  Each line: {"env_id": "...", "docs_path": "..."}."""
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def seed_jobs(manifest: list[dict]) -> None:
    """Post one generate-queue message per manifest entry."""
    log.info("Seeding %d environment jobs", len(manifest))
    for entry in manifest:
        msg = {
            "env_id": entry["env_id"],
            "iteration": 1,
            "docs_source": entry.get("docs_path", ""),
        }
        send_message(GENERATE_QUEUE_URL, msg)
        log.info("  queued %s (docs: %s)", entry["env_id"], entry.get("docs_path", ""))
    log.info("All %d jobs seeded to generate-queue", len(manifest))


def monitor(total_envs: int) -> None:
    """Block until all environments report completion via pipeline-done-queue."""
    completed: dict[str, dict] = {}
    log.info(
        "Monitoring pipeline-done-queue for %d completions ...", total_envs
    )

    while len(completed) < total_envs:
        result = receive_message(PIPELINE_DONE_QUEUE_URL, visibility_timeout=60)
        if result is None:
            log.info(
                "Progress: %d / %d complete", len(completed), total_envs
            )
            continue

        body, receipt = result
        env_id = body["env_id"]
        if env_id not in completed:
            completed[env_id] = body
            log.info(
                "✓ %s done (iteration=%d, pass_rate=%.1f%%) — %d/%d",
                env_id,
                body.get("final_iteration", "?"),
                body.get("pass_rate", 0),
                len(completed),
                total_envs,
            )
        delete_message(PIPELINE_DONE_QUEUE_URL, receipt)

    # Final summary
    log.info("=" * 60)
    log.info("All %d environments completed!", total_envs)
    avg_pass = sum(c.get("pass_rate", 0) for c in completed.values()) / len(completed)
    log.info("Average pass rate: %.1f%%", avg_pass)

    summary_path = f"/tmp/pipeline_summary_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(summary_path, "w") as f:
        json.dump(
            {
                "total": total_envs,
                "completed": len(completed),
                "average_pass_rate": round(avg_pass, 1),
                "environments": completed,
            },
            f,
            indent=2,
        )
    log.info("Summary written to %s", summary_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline orchestrator")
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help="Path to env_manifest.jsonl (default: %(default)s)",
    )
    parser.add_argument(
        "--monitor-only",
        action="store_true",
        help="Skip seeding, only monitor completions",
    )
    parser.add_argument(
        "--total-envs",
        type=int,
        default=None,
        help="Override env count for --monitor-only (default: read from manifest)",
    )
    args = parser.parse_args()

    if not GENERATE_QUEUE_URL or not PIPELINE_DONE_QUEUE_URL:
        log.error(
            "Set GENERATE_QUEUE_URL and PIPELINE_DONE_QUEUE_URL env vars"
        )
        sys.exit(1)

    if not args.monitor_only:
        manifest = load_manifest(args.manifest)
        if not manifest:
            log.error("Manifest is empty: %s", args.manifest)
            sys.exit(1)
        seed_jobs(manifest)
        total = args.total_envs or len(manifest)
    else:
        if not args.total_envs:
            log.error("--monitor-only requires --total-envs")
            sys.exit(1)
        total = args.total_envs

    monitor(total)


if __name__ == "__main__":
    main()
