#!/usr/bin/env bash
# Move the Sophia execution clone to a new pinned commit.
#
# Usage:
#   export CLIMRR_REPO_ROOT=<absolute path of the execution clone>
#   bash scripts/sophia_pull_pinned.sh <commit-sha>
#
# Refuses to run if the working tree has local changes: this clone is
# pull-only, so local modifications mean something is wrong and would be
# silently discarded by a checkout.
set -euo pipefail

COMMIT_SHA="${1:-}"
if [[ -z "${COMMIT_SHA}" ]]; then
  echo "ERROR: a commit SHA is required as \$1." >&2
  echo "Usage: bash scripts/sophia_pull_pinned.sh <commit-sha>" >&2
  exit 2
fi

: "${CLIMRR_REPO_ROOT:?ERROR: set CLIMRR_REPO_ROOT to the absolute path of the execution clone}"

if [[ ! -d "${CLIMRR_REPO_ROOT}/.git" ]]; then
  echo "ERROR: no Git repository at ${CLIMRR_REPO_ROOT}." >&2
  echo "Run scripts/sophia_bootstrap.sh first." >&2
  exit 2
fi

cd "${CLIMRR_REPO_ROOT}"

# Re-assert pull-only on every run (decision D-003): cheap, and it repairs the
# clone if the push URL was ever restored by hand.
git remote set-url --push origin DISABLED
echo "==> Push URL: $(git remote get-url --push origin)"

# --- refuse to clobber local changes --------------------------------------
DIRTY="$(git status --porcelain --untracked-files=no)"
if [[ -n "${DIRTY}" ]]; then
  echo "ERROR: working tree has local changes. This clone is pull-only." >&2
  echo "${DIRTY}" >&2
  echo >&2
  echo "Save anything you need, restore the tree, and re-run." >&2
  exit 1
fi

echo "==> Fetching."
git fetch --all --tags --prune

echo "==> Checking out ${COMMIT_SHA}."
git checkout --detach "${COMMIT_SHA}"

# --- verify clean after checkout ------------------------------------------
AFTER="$(git status --porcelain --untracked-files=no)"
if [[ -n "${AFTER}" ]]; then
  echo "ERROR: working tree is not clean after checkout." >&2
  echo "${AFTER}" >&2
  exit 1
fi

echo "==> HEAD: $(git rev-parse HEAD)"
echo "==> Working tree clean. Pinned checkout complete."
