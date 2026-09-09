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

# --- explain the one collision that happens in practice ------------------
# Run records generated on this host are untracked here, but once they have been
# copied back and committed from the authoring clone they are *tracked* in the
# next pinned commit --- so checking that commit out would overwrite them and git
# refuses. That refusal is correct and this function does not override it: it
# only says which files collided, whether the pinned commit already carries the
# identical bytes, and what to remove.
explain_untracked_collision() {
  local commit="$1" output="$2"
  local file committed_hash local_hash
  local -a identical=() differing=() absent=()

  # git lists one offending path per line, tab-indented.
  while IFS= read -r file; do
    [[ -z "${file}" ]] && continue
    if ! committed_hash="$(git rev-parse --verify --quiet "${commit}:${file}")"; then
      absent+=("${file}")
      continue
    fi
    local_hash="$(git hash-object -- "${file}")"
    if [[ "${local_hash}" == "${committed_hash}" ]]; then
      identical+=("${file}")
    else
      differing+=("${file}")
    fi
  done < <(printf '%s\n' "${output}" | sed -n 's/^\t\(.*\)$/\1/p')

  echo >&2
  echo "==> Untracked files here collide with files tracked in ${COMMIT_SHA}." >&2

  if [[ ${#identical[@]} -gt 0 ]]; then
    echo >&2
    echo "These are BYTE-IDENTICAL to what the pinned commit tracks --- they are your" >&2
    echo "own run records, already copied back and committed. Deleting them loses" >&2
    echo "nothing; the checkout restores the same bytes:" >&2
    printf '  %s\n' "${identical[@]}" >&2
    echo >&2
    echo "Remove them and re-run this script:" >&2
    echo >&2
    echo "  rm -f ${identical[*]}" >&2
  fi

  if [[ ${#differing[@]} -gt 0 ]]; then
    echo >&2
    echo "These DIFFER from the versions the pinned commit tracks. Do not delete them" >&2
    echo "until you know why --- copy them somewhere safe and report the difference:" >&2
    printf '  %s\n' "${differing[@]}" >&2
  fi

  if [[ ${#absent[@]} -gt 0 ]]; then
    echo >&2
    echo "These are not in the pinned commit at all, so this script cannot judge them:" >&2
    printf '  %s\n' "${absent[@]}" >&2
  fi

  echo >&2
  echo "Nothing has been deleted. This script never removes a file." >&2
}

echo "==> Checking out ${COMMIT_SHA}."
set +e
CHECKOUT_OUTPUT="$(git checkout --detach "${COMMIT_SHA}" 2>&1)"
CHECKOUT_RC=$?
set -e
printf '%s\n' "${CHECKOUT_OUTPUT}"
if [[ ${CHECKOUT_RC} -ne 0 ]]; then
  if grep -q "untracked working tree files would be overwritten" <<<"${CHECKOUT_OUTPUT}"; then
    explain_untracked_collision "${COMMIT_SHA}" "${CHECKOUT_OUTPUT}"
  fi
  exit "${CHECKOUT_RC}"
fi

# --- verify clean after checkout ------------------------------------------
AFTER="$(git status --porcelain --untracked-files=no)"
if [[ -n "${AFTER}" ]]; then
  echo "ERROR: working tree is not clean after checkout." >&2
  echo "${AFTER}" >&2
  exit 1
fi

echo "==> HEAD: $(git rev-parse HEAD)"
echo "==> Working tree clean. Pinned checkout complete."
