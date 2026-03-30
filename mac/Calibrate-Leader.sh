#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${LEKIWI_ENV_NAME:-lekiwi-homekit}"
LEADER_PORT="${LEKIWI_LEADER_PORT:-auto}"
CONDA_SH="${HOME}/miniforge3/etc/profile.d/conda.sh"

if [[ ! -f "${CONDA_SH}" ]]; then
  echo "Could not find ${CONDA_SH}. Run ./mac/Setup-Mac.sh first."
  exit 1
fi

source "${CONDA_SH}"
conda activate "${ENV_NAME}"

python "${REPO_ROOT}/scripts/calibrate_leader.py" --leader-port "${LEADER_PORT}"
