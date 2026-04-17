#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${LEKIWI_ENV_NAME:-lekiwi-homekit}"
ROBOT_IP="${LEKIWI_REMOTE_IP:-10.42.0.1}"
LEADER_PORT="${LEKIWI_LEADER_PORT:-auto}"
CONDA_EXE="${CONDA_EXE:-$(command -v conda || true)}"

if [[ -z "${CONDA_EXE}" ]]; then
  echo "Could not find 'conda' on PATH. Run ./mac/Setup-Mac.sh first."
  exit 1
fi

CONDA_BASE="$("${CONDA_EXE}" info --base)"
CONDA_SH="${CONDA_BASE}/etc/profile.d/conda.sh"

if [[ ! -f "${CONDA_SH}" ]]; then
  echo "Could not find ${CONDA_SH}. Run ./mac/Setup-Mac.sh first."
  exit 1
fi

source "${CONDA_SH}"
conda activate "${ENV_NAME}"

python "${REPO_ROOT}/scripts/run_manual_control.py" --robot-ip "${ROBOT_IP}" --leader-port "${LEADER_PORT}"
