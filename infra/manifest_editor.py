#!/usr/bin/env python3
"""Simple web UI for editing infra/env_manifest.jsonl.

Browse available docs folders, create environments, and assign docs
via point-and-click.

Usage:
    python infra/manifest_editor.py                # http://localhost:5555
    python infra/manifest_editor.py --port 8080
"""

import argparse
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = REPO_DIR / "apps"
MANIFEST_PATH = REPO_DIR / "infra" / "env_manifest.jsonl"


def scan_docs_tree() -> list[dict]:
    """Walk apps/*/docs/ and return a tree structure of available doc folders."""
    nodes = []
    for app_dir in sorted(APPS_DIR.iterdir()):
        docs_dir = app_dir / "docs"
        if not docs_dir.is_dir():
            continue
        app_name = app_dir.name
        for root, dirs, _files in os.walk(docs_dir):
            dirs.sort()
            rel = os.path.relpath(root, REPO_DIR)
            depth = rel.replace(f"apps/{app_name}/docs", "").count(os.sep)
            nodes.append({
                "path": rel,
                "label": os.path.basename(root),
                "app": app_name,
                "depth": depth,
            })
    return nodes


def load_manifest() -> list[dict]:
    if not MANIFEST_PATH.exists():
        return []
    entries = []
    for line in MANIFEST_PATH.read_text().splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def save_manifest(entries: list[dict]) -> None:
    with open(MANIFEST_PATH, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Env Manifest Editor</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f1117; color: #e1e4e8; display: flex; height: 100vh; }

  /* Left panel: docs browser */
  .panel-left { width: 380px; border-right: 1px solid #2d333b; display: flex;
                flex-direction: column; flex-shrink: 0; }
  .panel-left h2 { padding: 16px; font-size: 14px; color: #8b949e;
                    border-bottom: 1px solid #2d333b; }
  .search-box { padding: 8px 16px; border-bottom: 1px solid #2d333b; }
  .search-box input { width: 100%; padding: 6px 10px; background: #161b22;
                       border: 1px solid #30363d; border-radius: 6px; color: #e1e4e8;
                       font-size: 13px; outline: none; }
  .search-box input:focus { border-color: #58a6ff; }
  .docs-tree { flex: 1; overflow-y: auto; padding: 8px 0; }
  .doc-node { padding: 4px 12px; cursor: pointer; font-size: 13px;
              white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
              display: flex; align-items: center; gap: 6px; }
  .doc-node:hover { background: #1c2128; }
  .doc-node.selected { background: #1f6feb33; color: #58a6ff; }
  .doc-node .icon { flex-shrink: 0; font-size: 12px; color: #8b949e; }
  .doc-node .path-hint { color: #484f58; font-size: 11px; margin-left: auto;
                          flex-shrink: 0; padding-left: 8px; }
  .app-header { padding: 8px 12px; font-size: 12px; font-weight: 600;
                color: #58a6ff; text-transform: uppercase; letter-spacing: 0.5px;
                position: sticky; top: 0; background: #0f1117; }

  /* Right panel: manifest */
  .panel-right { flex: 1; display: flex; flex-direction: column; }
  .toolbar { padding: 12px 20px; border-bottom: 1px solid #2d333b;
             display: flex; align-items: center; gap: 12px; }
  .toolbar h2 { font-size: 14px; color: #8b949e; }
  .toolbar .spacer { flex: 1; }
  .btn { padding: 6px 14px; border: 1px solid #30363d; border-radius: 6px;
         background: #21262d; color: #e1e4e8; font-size: 13px; cursor: pointer; }
  .btn:hover { background: #30363d; }
  .btn-primary { background: #238636; border-color: #2ea043; }
  .btn-primary:hover { background: #2ea043; }
  .btn-danger { background: #da3633; border-color: #f85149; }
  .btn-danger:hover { background: #f85149; }
  .btn-sm { padding: 3px 8px; font-size: 12px; }

  .manifest-list { flex: 1; overflow-y: auto; padding: 12px 20px; }
  .env-row { display: flex; align-items: center; gap: 10px; padding: 8px 12px;
             border: 1px solid #21262d; border-radius: 8px; margin-bottom: 8px;
             background: #161b22; }
  .env-row:hover { border-color: #30363d; }
  .env-id { font-weight: 600; font-size: 14px; min-width: 80px; }
  .env-docs { flex: 1; font-size: 13px; color: #8b949e; overflow: hidden;
              text-overflow: ellipsis; white-space: nowrap; }
  .env-docs.has-docs { color: #7ee787; }
  .env-docs.no-docs { color: #484f58; font-style: italic; }

  .empty-state { text-align: center; padding: 60px 20px; color: #484f58; }
  .empty-state p { margin-bottom: 16px; }

  .counter { font-size: 12px; color: #8b949e; padding: 2px 8px;
             background: #21262d; border-radius: 10px; }

  /* Add env modal */
  .modal-overlay { display: none; position: fixed; inset: 0; background: #000a;
                   z-index: 100; align-items: center; justify-content: center; }
  .modal-overlay.active { display: flex; }
  .modal { background: #161b22; border: 1px solid #30363d; border-radius: 12px;
           padding: 24px; width: 420px; }
  .modal h3 { margin-bottom: 16px; }
  .modal label { font-size: 13px; color: #8b949e; display: block; margin-bottom: 4px; }
  .modal input { width: 100%; padding: 8px 10px; background: #0d1117;
                 border: 1px solid #30363d; border-radius: 6px; color: #e1e4e8;
                 font-size: 14px; margin-bottom: 16px; outline: none; }
  .modal input:focus { border-color: #58a6ff; }
  .modal-actions { display: flex; gap: 8px; justify-content: flex-end; }

  .toast { position: fixed; bottom: 20px; right: 20px; background: #238636;
           color: #fff; padding: 10px 20px; border-radius: 8px; font-size: 13px;
           display: none; z-index: 200; }
  .toast.show { display: block; }
</style>
</head>
<body>

<!-- Left: Docs browser -->
<div class="panel-left">
  <h2>Docs Browser</h2>
  <div class="search-box">
    <input type="text" id="searchInput" placeholder="Filter docs folders...">
  </div>
  <div class="docs-tree" id="docsTree"></div>
</div>

<!-- Right: Manifest editor -->
<div class="panel-right">
  <div class="toolbar">
    <h2>Environments</h2>
    <span class="counter" id="envCount">0</span>
    <span class="spacer"></span>
    <button class="btn" id="addBatchBtn">+ Batch Add</button>
    <button class="btn" id="addEnvBtn">+ Add Env</button>
    <button class="btn btn-primary" id="saveBtn">Save Manifest</button>
  </div>
  <div class="manifest-list" id="manifestList"></div>
</div>

<!-- Add env modal -->
<div class="modal-overlay" id="addModal">
  <div class="modal">
    <h3 id="modalTitle">Add Environment</h3>
    <label>Environment ID</label>
    <input type="text" id="envIdInput" placeholder="env-001">
    <label>Docs Path (click a folder on the left, or type manually)</label>
    <input type="text" id="docsPathInput" placeholder="apps/gitlab-org-management/docs/...">
    <div class="modal-actions">
      <button class="btn" id="cancelModal">Cancel</button>
      <button class="btn btn-primary" id="confirmModal">Add</button>
    </div>
  </div>
</div>

<!-- Batch add modal -->
<div class="modal-overlay" id="batchModal">
  <div class="modal">
    <h3>Batch Add Environments</h3>
    <label>Start number</label>
    <input type="number" id="batchStart" value="1" min="1">
    <label>Count</label>
    <input type="number" id="batchCount" value="10" min="1" max="500">
    <p style="font-size:12px;color:#8b949e;margin-bottom:16px;">
      Creates env-001, env-002, ... without docs assigned. Assign docs by clicking
      a folder on the left while an env row is selected.
    </p>
    <div class="modal-actions">
      <button class="btn" id="cancelBatch">Cancel</button>
      <button class="btn btn-primary" id="confirmBatch">Create</button>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let manifest = [];
let docsNodes = [];
let selectedEnvIdx = null;

// --- API ---
async function fetchDocs() {
  const r = await fetch('/api/docs');
  docsNodes = await r.json();
  renderDocs();
}

async function fetchManifest() {
  const r = await fetch('/api/manifest');
  manifest = await r.json();
  renderManifest();
}

async function saveManifest() {
  await fetch('/api/manifest', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(manifest),
  });
  showToast('Manifest saved!');
}

// --- Render docs tree ---
function renderDocs(filter = '') {
  const tree = document.getElementById('docsTree');
  const lc = filter.toLowerCase();
  let html = '';
  let currentApp = '';

  for (const node of docsNodes) {
    if (lc && !node.path.toLowerCase().includes(lc) && !node.label.toLowerCase().includes(lc)) continue;
    if (node.app !== currentApp) {
      currentApp = node.app;
      html += `<div class="app-header">${currentApp}</div>`;
    }
    const indent = 12 + node.depth * 16;
    const sel = selectedEnvIdx !== null && manifest[selectedEnvIdx]?.docs_path === node.path ? ' selected' : '';
    html += `<div class="doc-node${sel}" data-path="${node.path}" style="padding-left:${indent}px">`
          + `<span class="icon">&#128193;</span>${node.label}`
          + `<span class="path-hint">${node.depth > 0 ? '' : node.path}</span></div>`;
  }
  tree.innerHTML = html || '<div style="padding:20px;color:#484f58">No matches</div>';

  // Click handler
  tree.querySelectorAll('.doc-node').forEach(el => {
    el.addEventListener('click', () => {
      const path = el.dataset.path;
      // If an env is selected, assign this docs path to it
      if (selectedEnvIdx !== null && selectedEnvIdx < manifest.length) {
        manifest[selectedEnvIdx].docs_path = path;
        renderManifest();
        renderDocs(document.getElementById('searchInput').value);
      } else {
        // Pre-fill the add modal
        document.getElementById('docsPathInput').value = path;
      }
    });
  });
}

// --- Render manifest ---
function renderManifest() {
  const list = document.getElementById('manifestList');
  document.getElementById('envCount').textContent = manifest.length;

  if (manifest.length === 0) {
    list.innerHTML = '<div class="empty-state"><p>No environments yet.</p>'
                   + '<p>Click "+ Add Env" or "+ Batch Add" to get started.</p></div>';
    return;
  }

  let html = '';
  for (let i = 0; i < manifest.length; i++) {
    const e = manifest[i];
    const sel = i === selectedEnvIdx ? 'border-color:#58a6ff;' : '';
    const docsClass = e.docs_path ? 'has-docs' : 'no-docs';
    const docsText = e.docs_path || 'No docs assigned — click a folder on the left';
    html += `<div class="env-row" data-idx="${i}" style="${sel}">`
          + `<span class="env-id">${e.env_id}</span>`
          + `<span class="env-docs ${docsClass}" title="${e.docs_path || ''}">${docsText}</span>`
          + `<button class="btn btn-sm" data-action="select" data-idx="${i}">`
          + `${i === selectedEnvIdx ? '&#10003; Selected' : 'Select'}</button>`
          + `<button class="btn btn-sm btn-danger" data-action="remove" data-idx="${i}">&#10005;</button>`
          + `</div>`;
  }
  list.innerHTML = html;

  list.querySelectorAll('button[data-action="select"]').forEach(btn => {
    btn.addEventListener('click', (ev) => {
      ev.stopPropagation();
      const idx = parseInt(btn.dataset.idx);
      selectedEnvIdx = selectedEnvIdx === idx ? null : idx;
      renderManifest();
      renderDocs(document.getElementById('searchInput').value);
    });
  });

  list.querySelectorAll('button[data-action="remove"]').forEach(btn => {
    btn.addEventListener('click', (ev) => {
      ev.stopPropagation();
      const idx = parseInt(btn.dataset.idx);
      manifest.splice(idx, 1);
      if (selectedEnvIdx === idx) selectedEnvIdx = null;
      else if (selectedEnvIdx > idx) selectedEnvIdx--;
      renderManifest();
    });
  });
}

// --- Modals ---
document.getElementById('addEnvBtn').addEventListener('click', () => {
  const next = manifest.length + 1;
  document.getElementById('envIdInput').value = `env-${String(next).padStart(3, '0')}`;
  document.getElementById('docsPathInput').value = '';
  document.getElementById('addModal').classList.add('active');
  document.getElementById('envIdInput').focus();
});

document.getElementById('cancelModal').addEventListener('click', () => {
  document.getElementById('addModal').classList.remove('active');
});

document.getElementById('confirmModal').addEventListener('click', () => {
  const envId = document.getElementById('envIdInput').value.trim();
  const docs = document.getElementById('docsPathInput').value.trim();
  if (!envId) return;
  if (manifest.some(e => e.env_id === envId)) {
    alert(`${envId} already exists`);
    return;
  }
  manifest.push({ env_id: envId, docs_path: docs });
  document.getElementById('addModal').classList.remove('active');
  renderManifest();
});

document.getElementById('addBatchBtn').addEventListener('click', () => {
  const next = manifest.length + 1;
  document.getElementById('batchStart').value = next;
  document.getElementById('batchCount').value = 10;
  document.getElementById('batchModal').classList.add('active');
});

document.getElementById('cancelBatch').addEventListener('click', () => {
  document.getElementById('batchModal').classList.remove('active');
});

document.getElementById('confirmBatch').addEventListener('click', () => {
  const start = parseInt(document.getElementById('batchStart').value);
  const count = parseInt(document.getElementById('batchCount').value);
  for (let i = 0; i < count; i++) {
    const num = start + i;
    const envId = `env-${String(num).padStart(3, '0')}`;
    if (!manifest.some(e => e.env_id === envId)) {
      manifest.push({ env_id: envId, docs_path: '' });
    }
  }
  document.getElementById('batchModal').classList.remove('active');
  renderManifest();
});

document.getElementById('saveBtn').addEventListener('click', saveManifest);

document.getElementById('searchInput').addEventListener('input', (e) => {
  renderDocs(e.target.value);
});

// Close modals on overlay click
['addModal', 'batchModal'].forEach(id => {
  document.getElementById(id).addEventListener('click', (e) => {
    if (e.target === document.getElementById(id)) {
      document.getElementById(id).classList.remove('active');
    }
  });
});

// Keyboard: Enter to confirm modals, Escape to close
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
  }
  if (e.key === 'Enter' && document.getElementById('addModal').classList.contains('active')) {
    document.getElementById('confirmModal').click();
  }
});

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}

// --- Init ---
fetchDocs();
fetchManifest();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/" or path == "":
            self._respond(200, "text/html", HTML_PAGE)
        elif path == "/api/docs":
            docs = scan_docs_tree()
            self._respond(200, "application/json", json.dumps(docs))
        elif path == "/api/manifest":
            entries = load_manifest()
            self._respond(200, "application/json", json.dumps(entries))
        else:
            self._respond(404, "text/plain", "Not found")

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/manifest":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            entries = json.loads(body)
            save_manifest(entries)
            self._respond(200, "application/json", json.dumps({"ok": True}))
        else:
            self._respond(404, "text/plain", "Not found")

    def _respond(self, code, content_type, body):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Quieter logging
        pass


def main():
    parser = argparse.ArgumentParser(description="Env manifest editor UI")
    parser.add_argument("--port", type=int, default=5555)
    args = parser.parse_args()

    server = HTTPServer(("0.0.0.0", args.port), Handler)
    print(f"Manifest editor running at http://localhost:{args.port}")
    print(f"Manifest file: {MANIFEST_PATH}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")


if __name__ == "__main__":
    main()
