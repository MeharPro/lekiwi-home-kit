#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${1:-lekiwi-homekit}"
CONDA_SH="${HOME}/miniforge3/etc/profile.d/conda.sh"

if [[ ! -f "${CONDA_SH}" ]]; then
  echo "Could not find ${CONDA_SH}. Install Miniforge first."
  exit 1
fi

source "${CONDA_SH}"

if ! conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
  conda create -y -n "${ENV_NAME}" python=3.12
fi

conda activate "${ENV_NAME}"
python -m pip install --upgrade pip
python -m pip install -e "${REPO_ROOT}/vendor/lerobot[lekiwi]"

mkdir -p "${HOME}/.cache/huggingface/lerobot/calibration"
cp -R "${REPO_ROOT}/assets/calibration/." "${HOME}/.cache/huggingface/lerobot/calibration/"

echo
echo "Setup complete."
echo "Start manual control with:"
echo "  ./mac/Start-Manual-Control.sh"
echo
echo "Calibrate the leader with:"
echo "  ./mac/Calibrate-Leader.sh"
