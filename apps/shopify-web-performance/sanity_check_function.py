#!/usr/bin/env python3
"""
Sanity check for Shopify Web Performance Dashboard function-test tasks.

For each task, directly applies the expected end-state (bypassing the agent),
then runs the verifier and asserts it passes.

Usage:
    python3 sanity_check_function.py                      # All tasks, sequential
    python3 sanity_check_function.py --workers N           # N parallel environments
    python3 sanity_check_function.py --task-id task_5      # Single task
    python3 sanity_check_function.py --port 9000           # Custom base port
"""

import argparse
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

APP_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Seed state generation via Node.js
# ---------------------------------------------------------------------------

_SEED_STATE_JS = r"""
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(process.argv[1], 'utf8');
vm.runInThisContext(code);

const state = {
    _seedVersion: SEED_DATA_VERSION,
    storeInfo: JSON.parse(JSON.stringify(STORE_INFO)),
    currentUser: JSON.parse(JSON.stringify(CURRENT_USER)),
    themes: JSON.parse(JSON.stringify(THEMES)),
    apps: JSON.parse(JSON.stringify(APPS)),
    tagManagerTags: JSON.parse(JSON.stringify(TAG_MANAGER_TAGS)),
    pages: JSON.parse(JSON.stringify(PAGES)),
    pageTypes: JSON.parse(JSON.stringify(PAGE_TYPES)),
    pagePerformance: JSON.parse(JSON.stringify(PAGE_PERFORMANCE)),
    pageTypePerformance: JSON.parse(JSON.stringify(PAGE_TYPE_PERFORMANCE)),
    performanceEvents: JSON.parse(JSON.stringify(PERFORMANCE_EVENTS)),
    sessionsByDevice: JSON.parse(JSON.stringify(SESSIONS_BY_DEVICE)),
    overallPerformance: JSON.parse(JSON.stringify(OVERALL_PERFORMANCE)),
    recommendations: JSON.parse(JSON.stringify(RECOMMENDATIONS)),
    reports: JSON.parse(JSON.stringify(REPORTS)),
    settings: JSON.parse(JSON.stringify(SETTINGS)),
    lcpOverTimeDesktop: JSON.parse(JSON.stringify(LCP_OVER_TIME_DESKTOP)),
    lcpOverTimeMobile: JSON.parse(JSON.stringify(LCP_OVER_TIME_MOBILE)),
    inpOverTimeDesktop: JSON.parse(JSON.stringify(INP_OVER_TIME_DESKTOP)),
    inpOverTimeMobile: JSON.parse(JSON.stringify(INP_OVER_TIME_MOBILE)),
    clsOverTimeDesktop: JSON.parse(JSON.stringify(CLS_OVER_TIME_DESKTOP)),
    clsOverTimeMobile: JSON.parse(JSON.stringify(CLS_OVER_TIME_MOBILE)),
};
process.stdout.write(JSON.stringify(state));
"""


def generate_seed_state():
    """Use Node.js to evaluate data.js and produce the seed state JSON."""
    data_js = str(APP_DIR / "js" / "data.js")
    result = subprocess.run(
        ["node", "-e", _SEED_STATE_JS, data_js],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to generate seed state:\n{result.stderr}")
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Entity lookup helpers
# ---------------------------------------------------------------------------

def find_app_by_name(state, name):
    for a in state["apps"]:
        if a["name"] == name:
            return a
    raise ValueError(f"App not found: {name!r}")


def find_app_containing(state, fragment):
    for a in state["apps"]:
        if fragment in a["name"]:
            return a
    raise ValueError(f"App containing {fragment!r} not found")


def find_tag_by_name(state, name):
    for t in state["tagManagerTags"]:
        if t["name"] == name:
            return t
    raise ValueError(f"Tag not found: {name!r}")


def find_theme_by_name(state, name):
    for t in state["themes"]:
        if t["name"] == name:
            return t
    raise ValueError(f"Theme not found: {name!r}")


def find_rec_by_title(state, title):
    for r in state["recommendations"]:
        if r["title"] == title:
            return r
    raise ValueError(f"Recommendation not found: {title!r}")


def find_rec_by_id(state, rec_id):
    for r in state["recommendations"]:
        if r["id"] == rec_id:
            return r
    raise ValueError(f"Recommendation not found: {rec_id!r}")


# ---------------------------------------------------------------------------
# Solve functions — one per task
# ---------------------------------------------------------------------------

def solve_task_1(state):
    """Disable Klaviyo app."""
    app = find_app_by_name(state, "Klaviyo: Email Marketing & SMS")
    app["status"] = "disabled"
    app["loadsOnStorefront"] = False


def solve_task_2(state):
    """Enable SEO Manager app."""
    app = find_app_by_name(state, "SEO Manager")
    app["status"] = "active"
    # scriptsCount is 0, so loadsOnStorefront stays False
    app["loadsOnStorefront"] = app["scriptsCount"] > 0


def solve_task_3(state):
    """Remove Hotjar app."""
    state["apps"] = [a for a in state["apps"] if a["name"] != "Hotjar Heatmaps & Recordings"]


def solve_task_4(state):
    """Disable Recharge Subscriptions app."""
    app = find_app_by_name(state, "Recharge Subscriptions")
    app["status"] = "disabled"
    app["loadsOnStorefront"] = False


def solve_task_5(state):
    """Enable Infinite Options app."""
    app = find_app_by_name(state, "Infinite Options")
    app["status"] = "active"
    app["loadsOnStorefront"] = app["scriptsCount"] > 0


def solve_task_6(state):
    """Remove Back in Stock Alerts app."""
    state["apps"] = [a for a in state["apps"] if a["name"] != "Back in Stock Alerts"]


def solve_task_7(state):
    """Disable Privy app."""
    app = find_app_containing(state, "Privy")
    app["status"] = "disabled"
    app["loadsOnStorefront"] = False


def solve_task_8(state):
    """Remove Bold Product Options app."""
    state["apps"] = [a for a in state["apps"] if a["name"] != "Bold Product Options"]


def solve_task_9(state):
    """Activate Pinterest Tag."""
    tag = find_tag_by_name(state, "Pinterest Tag")
    tag["status"] = "active"


def solve_task_10(state):
    """Deactivate Google Analytics 4 tag."""
    tag = find_tag_by_name(state, "Google Analytics 4")
    tag["status"] = "inactive"


def solve_task_11(state):
    """Remove Snapchat Pixel tag."""
    state["tagManagerTags"] = [t for t in state["tagManagerTags"] if t["name"] != "Snapchat Pixel"]


def solve_task_12(state):
    """Activate Lucky Orange tag."""
    tag = find_tag_by_name(state, "Lucky Orange")
    tag["status"] = "active"


def solve_task_13(state):
    """Deactivate Hotjar Tracking tag."""
    tag = find_tag_by_name(state, "Hotjar Tracking")
    tag["status"] = "inactive"


def solve_task_14(state):
    """Remove Affirm Messaging tag."""
    state["tagManagerTags"] = [t for t in state["tagManagerTags"] if t["name"] != "Affirm Messaging"]


def solve_task_15(state):
    """Publish Dawn (backup) theme."""
    dawn = find_theme_by_name(state, "Dawn (backup)")
    horizon = find_theme_by_name(state, "Horizon - Outdoors")
    # Dawn becomes main
    dawn["role"] = "main"
    dawn["status"] = "published"
    # Previous main becomes unpublished
    horizon["role"] = "unpublished"
    horizon["status"] = "unpublished"
    state["settings"]["selectedThemeId"] = dawn["id"]


def solve_task_16(state):
    """Publish Prestige theme."""
    prestige = find_theme_by_name(state, "Prestige")
    horizon = find_theme_by_name(state, "Horizon - Outdoors")
    prestige["role"] = "main"
    prestige["status"] = "published"
    horizon["role"] = "unpublished"
    horizon["status"] = "unpublished"
    state["settings"]["selectedThemeId"] = prestige["id"]


def solve_task_17(state):
    """Disable animations on Horizon - Outdoors."""
    theme = find_theme_by_name(state, "Horizon - Outdoors")
    theme["hasAnimations"] = False


def solve_task_18(state):
    """Enable page transitions on Horizon - Outdoors."""
    theme = find_theme_by_name(state, "Horizon - Outdoors")
    theme["hasPageTransitions"] = True


def solve_task_19(state):
    """Disable animations on Prestige."""
    theme = find_theme_by_name(state, "Prestige")
    theme["hasAnimations"] = False


def solve_task_20(state):
    """Enable animations on Dawn (backup)."""
    theme = find_theme_by_name(state, "Dawn (backup)")
    theme["hasAnimations"] = True


def solve_task_21(state):
    """Disable page transitions on Prestige."""
    theme = find_theme_by_name(state, "Prestige")
    theme["hasPageTransitions"] = False


def solve_task_22(state):
    """Increase homepage sections for Horizon - Outdoors by 1."""
    theme = find_theme_by_name(state, "Horizon - Outdoors")
    theme["sectionsPerPage"]["home"] = 13  # seed is 12


def solve_task_23(state):
    """Decrease product sections for Horizon - Outdoors by 1."""
    theme = find_theme_by_name(state, "Horizon - Outdoors")
    theme["sectionsPerPage"]["product"] = 7  # seed is 8


def solve_task_24(state):
    """Increase blog sections for Prestige by 1."""
    theme = find_theme_by_name(state, "Prestige")
    theme["sectionsPerPage"]["blog"] = 8  # seed is 7


def solve_task_25(state):
    """Decrease homepage sections for Prestige by 1."""
    theme = find_theme_by_name(state, "Prestige")
    theme["sectionsPerPage"]["home"] = 17  # seed is 18


def solve_task_26(state):
    """Increase cart sections for Dawn (backup) by 1."""
    theme = find_theme_by_name(state, "Dawn (backup)")
    theme["sectionsPerPage"]["cart"] = 4  # seed is 3


def solve_task_27(state):
    """Decrease collection sections for Dawn (backup) by 1."""
    theme = find_theme_by_name(state, "Dawn (backup)")
    theme["sectionsPerPage"]["collection"] = 4  # seed is 5


def solve_task_28(state):
    """Resolve recommendation: Reduce the impact of third-party scripts."""
    rec = find_rec_by_title(state, "Reduce the impact of third-party scripts")
    rec["status"] = "resolved"


def solve_task_29(state):
    """Dismiss recommendation: Optimize large hero images on homepage."""
    rec = find_rec_by_title(state, "Optimize large hero images on homepage")
    rec["status"] = "dismissed"


def solve_task_30(state):
    """Reopen recommendation: Audit tag manager for unused tags."""
    rec = find_rec_by_title(state, "Audit tag manager for unused tags")
    rec["status"] = "open"


def solve_task_31(state):
    """Resolve recommendation: Reserve space for Privy pop-up banner."""
    rec = find_rec_by_title(state, "Reserve space for Privy pop-up banner")
    rec["status"] = "resolved"


def solve_task_32(state):
    """Dismiss recommendation: Reduce homepage sections."""
    rec = find_rec_by_title(state, "Reduce homepage sections")
    rec["status"] = "dismissed"


def solve_task_33(state):
    """Resolve recommendation: Evaluate Privy pop-up timing."""
    rec = find_rec_by_title(state, "Evaluate Privy pop-up timing")
    rec["status"] = "resolved"


def solve_task_34(state):
    """Dismiss recommendation: Preload web fonts."""
    rec = find_rec_by_title(state, "Preload web fonts")
    rec["status"] = "dismissed"


def solve_task_35(state):
    """Change date range to last_30_days."""
    state["settings"]["dateRange"] = "last_30_days"


def solve_task_36(state):
    """Change date range to today."""
    state["settings"]["dateRange"] = "today"


def solve_task_37(state):
    """Change device filter to mobile."""
    state["settings"]["deviceFilter"] = "mobile"


def solve_task_38(state):
    """Change device filter to desktop."""
    state["settings"]["deviceFilter"] = "desktop"


def solve_task_39(state):
    """Change date grouping to weekly."""
    state["settings"]["dateGrouping"] = "weekly"


def solve_task_40(state):
    """Change report percentile to p90."""
    state["settings"]["reportPercentile"] = "p90"


def solve_task_41(state):
    """Disable show annotations."""
    state["settings"]["showAnnotations"] = False


def solve_task_42(state):
    """Disable comparison."""
    state["settings"]["comparisonEnabled"] = False


def solve_task_43(state):
    """Disable alert on poor ranking."""
    state["settings"]["performanceAlerts"]["alertOnPoor"] = False


def solve_task_44(state):
    """Disable alert on degradation."""
    state["settings"]["performanceAlerts"]["alertOnDegradation"] = False


def solve_task_45(state):
    """Disable email alerts."""
    state["settings"]["performanceAlerts"]["emailAlerts"] = False


def solve_task_46(state):
    """Set LCP threshold to 3000."""
    state["settings"]["performanceAlerts"]["lcpThreshold"] = 3000


def solve_task_47(state):
    """Set INP threshold to 300."""
    state["settings"]["performanceAlerts"]["inpThreshold"] = 300


def solve_task_48(state):
    """Set CLS threshold to 0.25."""
    state["settings"]["performanceAlerts"]["clsThreshold"] = 0.25


def solve_task_49(state):
    """Set degradation percentage to 25."""
    state["settings"]["performanceAlerts"]["degradationPercent"] = 25


def solve_task_50(state):
    """Enable password protection."""
    state["storeInfo"]["passwordProtected"] = True


def solve_task_51(state):
    """Disable all 3 high-impact apps."""
    for name in ["Recharge Subscriptions", "Privy", "Hotjar"]:
        app = find_app_containing(state, name)
        app["status"] = "disabled"
        app["loadsOnStorefront"] = False


def solve_task_52(state):
    """Activate all inactive tags."""
    for name in ["Pinterest Tag", "Snapchat Pixel", "Lucky Orange"]:
        tag = find_tag_by_name(state, name)
        tag["status"] = "active"


def solve_task_53(state):
    """Resolve all high-priority recommendations."""
    for rec_id in ["rec_001", "rec_002", "rec_008"]:
        rec = find_rec_by_id(state, rec_id)
        rec["status"] = "resolved"


def solve_task_54(state):
    """Change date grouping to monthly and percentile to p95."""
    state["settings"]["dateGrouping"] = "monthly"
    state["settings"]["reportPercentile"] = "p95"


def solve_task_55(state):
    """Disable Klaviyo and remove Meta Pixel tag."""
    app = find_app_by_name(state, "Klaviyo: Email Marketing & SMS")
    app["status"] = "disabled"
    app["loadsOnStorefront"] = False
    state["tagManagerTags"] = [t for t in state["tagManagerTags"] if t["name"] != "Meta Pixel"]


# ---------------------------------------------------------------------------
# Solver registry
# ---------------------------------------------------------------------------

SOLVERS = {
    "task_1": solve_task_1,
    "task_2": solve_task_2,
    "task_3": solve_task_3,
    "task_4": solve_task_4,
    "task_5": solve_task_5,
    "task_6": solve_task_6,
    "task_7": solve_task_7,
    "task_8": solve_task_8,
    "task_9": solve_task_9,
    "task_10": solve_task_10,
    "task_11": solve_task_11,
    "task_12": solve_task_12,
    "task_13": solve_task_13,
    "task_14": solve_task_14,
    "task_15": solve_task_15,
    "task_16": solve_task_16,
    "task_17": solve_task_17,
    "task_18": solve_task_18,
    "task_19": solve_task_19,
    "task_20": solve_task_20,
    "task_21": solve_task_21,
    "task_22": solve_task_22,
    "task_23": solve_task_23,
    "task_24": solve_task_24,
    "task_25": solve_task_25,
    "task_26": solve_task_26,
    "task_27": solve_task_27,
    "task_28": solve_task_28,
    "task_29": solve_task_29,
    "task_30": solve_task_30,
    "task_31": solve_task_31,
    "task_32": solve_task_32,
    "task_33": solve_task_33,
    "task_34": solve_task_34,
    "task_35": solve_task_35,
    "task_36": solve_task_36,
    "task_37": solve_task_37,
    "task_38": solve_task_38,
    "task_39": solve_task_39,
    "task_40": solve_task_40,
    "task_41": solve_task_41,
    "task_42": solve_task_42,
    "task_43": solve_task_43,
    "task_44": solve_task_44,
    "task_45": solve_task_45,
    "task_46": solve_task_46,
    "task_47": solve_task_47,
    "task_48": solve_task_48,
    "task_49": solve_task_49,
    "task_50": solve_task_50,
    "task_51": solve_task_51,
    "task_52": solve_task_52,
    "task_53": solve_task_53,
    "task_54": solve_task_54,
    "task_55": solve_task_55,
}

# ---------------------------------------------------------------------------
# Task loading
# ---------------------------------------------------------------------------

def load_tasks():
    with open(APP_DIR / "function-tasks.json") as f:
        return json.load(f)


def load_verifier(verify_path):
    full_path = APP_DIR / verify_path
    spec = importlib.util.spec_from_file_location("verifier", full_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.verify


# ---------------------------------------------------------------------------
# Server management
# ---------------------------------------------------------------------------

def find_free_port(start=9500):
    port = start
    while port < start + 200:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(f"No free port found in range {start}-{start + 200}")


def seed_server(server_url, seed_state):
    resp = requests.put(
        f"{server_url}/api/state",
        json=seed_state,
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to seed server: HTTP {resp.status_code}")


def start_server(port):
    proc = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(port)],
        cwd=str(APP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        try:
            requests.get(f"http://localhost:{port}/", timeout=1)
            return proc
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(0.2)
    proc.kill()
    raise RuntimeError(f"Server failed to start on port {port}")


def stop_server(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


# ---------------------------------------------------------------------------
# Task runner
# ---------------------------------------------------------------------------

def run_single_task(task, server_url):
    task_id = task["id"]
    solver = SOLVERS.get(task_id)
    if not solver:
        return task_id, False, f"No solver defined for {task_id}"

    try:
        # 1. Reset to seed state
        resp = requests.post(f"{server_url}/api/reset")
        if resp.status_code != 200:
            return task_id, False, f"Reset failed: HTTP {resp.status_code}"
        time.sleep(0.3)

        # 2. Read seed state
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return task_id, False, f"Could not read state after reset: HTTP {resp.status_code}"
        state = resp.json()

        # 3. Apply the solve function
        solver(state)

        # 4. Write solved state back
        resp = requests.put(
            f"{server_url}/api/state",
            json=state,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            return task_id, False, f"Could not write state: HTTP {resp.status_code}"

        # 5. Run the verifier
        verify_fn = load_verifier(task["verify"])
        passed, message = verify_fn(server_url)
        return task_id, passed, message

    except Exception as e:
        return task_id, False, f"Exception: {e}"


def run_tasks_sequential(tasks, port, seed_state):
    proc = start_server(port)
    server_url = f"http://localhost:{port}"
    results = []
    try:
        seed_server(server_url, seed_state)
        for task in tasks:
            result = run_single_task(task, server_url)
            results.append(result)
            status = "\033[32m  PASS\033[0m" if result[1] else "\033[31m  FAIL\033[0m"
            print(f"{status}  {result[0]:12s}  {result[2]}")
    finally:
        stop_server(proc)
    return results


def run_tasks_parallel(tasks, workers, base_port, seed_state):
    results = []

    def worker_fn(task, port):
        proc = start_server(port)
        server_url = f"http://localhost:{port}"
        try:
            seed_server(server_url, seed_state)
            return run_single_task(task, server_url)
        finally:
            stop_server(proc)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for i, task in enumerate(tasks):
            port = base_port + i
            future = executor.submit(worker_fn, task, port)
            futures[future] = task["id"]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            status = "\033[32m  PASS\033[0m" if result[1] else "\033[31m  FAIL\033[0m"
            print(f"{status}  {result[0]:12s}  {result[2]}")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Shopify Web Performance function-task sanity check"
    )
    parser.add_argument("--task-id", type=str, help="Run a single task by ID")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers")
    parser.add_argument("--port", type=int, default=9500, help="Base port for servers")
    args = parser.parse_args()

    tasks = load_tasks()
    if args.task_id:
        tasks = [t for t in tasks if t["id"] == args.task_id]
        if not tasks:
            print(f"Task '{args.task_id}' not found.")
            sys.exit(1)

    print("Generating seed state from JS data...")
    seed_state = generate_seed_state()
    print(f"Running {len(tasks)} task(s)...\n")

    if args.workers <= 1:
        port = find_free_port(args.port)
        results = run_tasks_sequential(tasks, port, seed_state)
    else:
        results = run_tasks_parallel(tasks, args.workers, args.port, seed_state)

    # Summary
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    failed = [tid for tid, p, _ in results if not p]

    print(f"\n{passed}/{total} passed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
