#!/usr/bin/env bash
# Smoke test: verify all external dependencies before running a pipeline.
#
# Usage:
#   bash infra/smoke_test.sh                          # uses env vars from shell
#   bash infra/smoke_test.sh --model gemini
#   bash infra/smoke_test.sh --model gpt
#   source .env && bash infra/smoke_test.sh            # or source .env first locally

set -uo pipefail

MODEL="gemini"
S3_BUCKET="${MM_S3_BUCKET:-mirror-mirror-results}"
BRANCH="smoke-test-$$"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)     MODEL="$2";     shift 2 ;;
    --s3-bucket) S3_BUCKET="$2"; shift 2 ;;
    --branch)    BRANCH="$2";    shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

PASS=0
FAIL=0
SKIP=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }
skip() { echo "  SKIP: $1"; SKIP=$((SKIP + 1)); }

# ── 1. Model API ─────────────────────────────────────────────────────────

echo ""
echo "=== 1. Model API ($MODEL) ==="

case "$MODEL" in
  gemini)
    if [ -z "${GOOGLE_API_KEY:-}" ]; then
      fail "GOOGLE_API_KEY not set"
    else
      RESP=$(curl -s -w "\n%{http_code}" \
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GOOGLE_API_KEY}" \
        -H 'Content-Type: application/json' \
        -d '{"contents":[{"parts":[{"text":"Say hello in one word"}]}]}' \
        2>&1)
      HTTP_CODE=$(echo "$RESP" | tail -1)
      BODY=$(echo "$RESP" | sed '$d')
      if [ "$HTTP_CODE" = "200" ]; then
        SNIPPET=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['candidates'][0]['content']['parts'][0]['text'][:80])" 2>/dev/null || echo "(parse error)")
        pass "Gemini API responded: $SNIPPET"
      else
        fail "Gemini API returned HTTP $HTTP_CODE"
        echo "       $(echo "$BODY" | head -3)"
      fi
    fi
    ;;
  gpt)
    if [ -z "${OPENAI_API_KEY:-}" ]; then
      fail "OPENAI_API_KEY not set"
    else
      RESP=$(curl -s -w "\n%{http_code}" \
        "https://api.openai.com/v1/chat/completions" \
        -H "Authorization: Bearer ${OPENAI_API_KEY}" \
        -H 'Content-Type: application/json' \
        -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hello in one word"}],"max_tokens":10}' \
        2>&1)
      HTTP_CODE=$(echo "$RESP" | tail -1)
      BODY=$(echo "$RESP" | sed '$d')
      if [ "$HTTP_CODE" = "200" ]; then
        SNIPPET=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'][:80])" 2>/dev/null || echo "(parse error)")
        pass "OpenAI API responded: $SNIPPET"
      else
        fail "OpenAI API returned HTTP $HTTP_CODE"
        echo "       $(echo "$BODY" | head -3)"
      fi
    fi
    ;;
  claude)
    if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
      fail "ANTHROPIC_API_KEY not set"
    else
      RESP=$(curl -s -w "\n%{http_code}" \
        "https://api.anthropic.com/v1/messages" \
        -H "x-api-key: ${ANTHROPIC_API_KEY}" \
        -H "anthropic-version: 2023-06-01" \
        -H 'Content-Type: application/json' \
        -d '{"model":"claude-haiku-4-5-20251001","max_tokens":10,"messages":[{"role":"user","content":"Say hello in one word"}]}' \
        2>&1)
      HTTP_CODE=$(echo "$RESP" | tail -1)
      BODY=$(echo "$RESP" | sed '$d')
      if [ "$HTTP_CODE" = "200" ]; then
        SNIPPET=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['content'][0]['text'][:80])" 2>/dev/null || echo "(parse error)")
        pass "Anthropic API responded: $SNIPPET"
      else
        fail "Anthropic API returned HTTP $HTTP_CODE"
        echo "       $(echo "$BODY" | head -3)"
      fi
    fi
    ;;
  *)
    fail "Unknown model: $MODEL"
    ;;
esac

# ── 2. Claude CLI ────────────────────────────────────────────────────────

echo ""
echo "=== 2. Claude CLI ==="

if ! command -v claude &>/dev/null; then
  fail "claude CLI not found in PATH"
else
  # Check login status (unset CLAUDECODE to avoid nested-session block)
  AUTH=$(unset CLAUDECODE && claude auth status 2>&1 || true)
  if echo "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('loggedIn') else 1)" 2>/dev/null; then
    AUTH_EMAIL=$(echo "$AUTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('email','?'))" 2>/dev/null || echo "?")
    pass "Claude CLI authenticated ($AUTH_EMAIL)"
  else
    fail "Claude CLI not authenticated: $(echo "$AUTH" | head -1)"
  fi

  # Check permissions (--dangerously-skip-permissions)
  HELLO=$(unset CLAUDECODE && timeout 30 claude --dangerously-skip-permissions -p "Print exactly: SMOKE_OK" 2>&1 || true)
  if echo "$HELLO" | grep -q "SMOKE_OK"; then
    pass "Claude CLI runs with --dangerously-skip-permissions"
  else
    fail "Claude CLI did not produce expected output"
    echo "       $(echo "$HELLO" | tail -3)"
  fi
fi

# ── 3a. GitHub Token ─────────────────────────────────────────────────────

echo ""
echo "=== 3a. GitHub Token ==="

if [ -z "${GITHUB_TOKEN:-}" ]; then
  fail "GITHUB_TOKEN not set"
else
  GH_RESP=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    "https://api.github.com/user" 2>&1)
  GH_HTTP=$(echo "$GH_RESP" | tail -1)
  GH_BODY=$(echo "$GH_RESP" | sed '$d')
  if [ "$GH_HTTP" = "200" ]; then
    GH_USER=$(echo "$GH_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('login','?'))" 2>/dev/null || echo "?")
    pass "GitHub API authenticated as: $GH_USER"
  else
    fail "GitHub API returned HTTP $GH_HTTP"
    echo "       $(echo "$GH_BODY" | head -3)"
  fi

  # Test push access: create and delete a temporary branch
  REMOTE_URL=$(git remote get-url origin 2>/dev/null)
  # Extract owner/repo from SSH, HTTPS, or PAT-embedded URL
  REPO_SLUG=$(echo "$REMOTE_URL" | sed -E 's#(git@github\.com:|https://([^@]+@)?github\.com/)##; s/\.git$//')

  if [ -n "$REPO_SLUG" ]; then
    # Get default branch SHA
    DEFAULT_SHA=$(curl -s \
      -H "Authorization: token ${GITHUB_TOKEN}" \
      "https://api.github.com/repos/${REPO_SLUG}/git/refs/heads/main" 2>/dev/null \
      | python3 -c "import sys,json; print(json.load(sys.stdin)['object']['sha'])" 2>/dev/null || echo "")

    if [ -n "$DEFAULT_SHA" ]; then
      TEST_BRANCH="refs/heads/_smoke-test-delete-me-$$"
      # Create
      CREATE_HTTP=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"ref\":\"${TEST_BRANCH}\",\"sha\":\"${DEFAULT_SHA}\"}" \
        "https://api.github.com/repos/${REPO_SLUG}/git/refs" 2>/dev/null)

      if [ "$CREATE_HTTP" = "201" ]; then
        # Delete it immediately
        DEL_HTTP=$(curl -s -o /dev/null -w "%{http_code}" \
          -X DELETE \
          -H "Authorization: token ${GITHUB_TOKEN}" \
          "https://api.github.com/repos/${REPO_SLUG}/git/${TEST_BRANCH}" 2>/dev/null)
        if [ "$DEL_HTTP" = "204" ]; then
          pass "GitHub push access verified (created+deleted test branch)"
        else
          pass "GitHub branch created (cleanup returned HTTP $DEL_HTTP — non-critical)"
        fi
      else
        fail "GitHub push access denied (create branch returned HTTP $CREATE_HTTP)"
      fi
    else
      fail "Could not resolve main branch SHA for push test"
    fi
  else
    skip "Could not parse repo slug from remote URL"
  fi
fi

# ── 3b. AWS / S3 ─────────────────────────────────────────────────────────

echo ""
echo "=== 3b. AWS / S3 (bucket: $S3_BUCKET) ==="

if ! command -v aws &>/dev/null; then
  fail "aws CLI not found"
else
  CALLER=$(aws sts get-caller-identity --query 'Arn' --output text 2>&1)
  if [ $? -eq 0 ]; then
    pass "AWS credentials valid: $CALLER"
  else
    fail "AWS credentials invalid: $CALLER"
  fi

  # Test S3 write + read + delete
  TEST_KEY="_smoke-test-$$.txt"
  echo "smoke-test" | aws s3 cp - "s3://${S3_BUCKET}/${TEST_KEY}" 2>&1
  if [ $? -eq 0 ]; then
    CONTENT=$(aws s3 cp "s3://${S3_BUCKET}/${TEST_KEY}" - 2>/dev/null)
    if [ "$CONTENT" = "smoke-test" ]; then
      pass "S3 write+read to s3://${S3_BUCKET}/ works"
    else
      fail "S3 read-back mismatch (got: '$CONTENT')"
    fi
    aws s3 rm "s3://${S3_BUCKET}/${TEST_KEY}" 2>/dev/null
  else
    fail "S3 write to s3://${S3_BUCKET}/${TEST_KEY} failed"
  fi
fi

# ── Summary ───────────────────────────────────────────────────────────────

echo ""
echo "==========================================="
echo "  PASS: $PASS   FAIL: $FAIL   SKIP: $SKIP"
echo "==========================================="

if [ "$FAIL" -gt 0 ]; then
  echo "  Some checks failed — fix before running pipeline."
  exit 1
else
  echo "  All checks passed — ready to run pipeline."
  exit 0
fi
