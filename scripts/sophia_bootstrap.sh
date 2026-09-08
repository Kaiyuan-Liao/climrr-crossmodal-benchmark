#!/usr/bin/env bash
# Bootstrap the pull-only execution clone on Sophia and run the M0 checks.
#
# Usage:
#   export CLIMRR_REPO_ROOT=<absolute path for the execution clone>
#   export CLIMRR_SCRATCH_DIR=<absolute scratch path on Eagle>   # optional
#   bash scripts/sophia_bootstrap.sh <commit-sha>
#
# Every machine-specific path comes from an environment variable at run time.
# Nothing in this file is hard-coded to a machine, and nothing it writes into
# the clone is tracked by Git.
set -euo pipefail

COMMIT_SHA="${1:-}"
if [[ -z "${COMMIT_SHA}" ]]; then
  echo "ERROR: a commit SHA is required as \$1." >&2
  echo "Usage: bash scripts/sophia_bootstrap.sh <commit-sha>" >&2
  exit 2
fi

: "${CLIMRR_REPO_ROOT:?ERROR: set CLIMRR_REPO_ROOT to the absolute path for the execution clone}"
REMOTE_URL="${CLIMRR_REMOTE_URL:-git@github.com:Kaiyuan-Liao/climrr-crossmodal-benchmark.git}"
SCRATCH_DIR="${CLIMRR_SCRATCH_DIR:-${CLIMRR_REPO_ROOT}/scratch}"
VENV_DIR="${CLIMRR_REPO_ROOT}/.venv-sophia"

echo "==> Execution clone : ${CLIMRR_REPO_ROOT}"
echo "==> Pinned commit   : ${COMMIT_SHA}"

# --- 1. clone (or reuse) ---------------------------------------------------
if [[ -d "${CLIMRR_REPO_ROOT}/.git" ]]; then
  echo "==> Clone already exists; fetching."
  git -C "${CLIMRR_REPO_ROOT}" fetch --all --tags
else
  echo "==> Cloning."
  mkdir -p "$(dirname "${CLIMRR_REPO_ROOT}")"
  git clone "${REMOTE_URL}" "${CLIMRR_REPO_ROOT}"
fi

# --- 2. make this clone mechanically pull-only (decision D-003) ------------
# The SSH key on this host has write access to the remote, so policy alone is
# not enough: disable the push URL so an accidental push cannot succeed.
git -C "${CLIMRR_REPO_ROOT}" remote set-url --push origin DISABLED
echo "==> Push URL disabled: $(git -C "${CLIMRR_REPO_ROOT}" remote get-url --push origin)"

# --- 3. check out the pinned commit ---------------------------------------
git -C "${CLIMRR_REPO_ROOT}" checkout --detach "${COMMIT_SHA}"
echo "==> HEAD: $(git -C "${CLIMRR_REPO_ROOT}" rev-parse HEAD)"

# --- 4. environment (decision D-004) --------------------------------------
echo "==> Building venv over the ALCF conda base module."
module use /soft/modulefiles
module load conda
conda activate base
python -m venv --system-site-packages "${VENV_DIR}"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r "${CLIMRR_REPO_ROOT}/requirements.txt"
echo "==> Python: $(python -V)"

# --- 5. local path config, generated from the environment ------------------
# Written at run time from environment variables; never hard-coded, and
# gitignored so it can never be committed back.
CONFIG_FILE="${CLIMRR_REPO_ROOT}/config/local_paths.yaml"
sed \
  -e "s|<LOCAL_REPO_ROOT>|${CLIMRR_REPO_ROOT}|g" \
  -e "s|<LOCATION_LABEL>|sophia|g" \
  -e "s|<SOURCE_CSV_ABSOLUTE_PATH>|${CLIMRR_SOURCE_CSV:-<not present on this host>}|g" \
  -e "s|<SOURCE_METADATA_PDF_ABSOLUTE_PATH>|${CLIMRR_SOURCE_PDF:-<not present on this host>}|g" \
  -e "s|<SCRATCH_DIR>|${SCRATCH_DIR}|g" \
  "${CLIMRR_REPO_ROOT}/config/local_paths.example.yaml" > "${CONFIG_FILE}"
echo "==> Wrote ${CONFIG_FILE} (untracked)"

# --- 6. checks -------------------------------------------------------------
cd "${CLIMRR_REPO_ROOT}"
echo "==> pytest"
python -m pytest -q

echo "==> smoke test"
python scripts/smoke_test.py

echo "==> git status (must be clean)"
git status --porcelain --untracked-files=no

echo
echo "==> Run records produced (copy these back):"
ls -1t reports/runs/*sophia* 2>/dev/null | head -4 || echo "(none found -- report this)"
echo "==> Bootstrap complete."
