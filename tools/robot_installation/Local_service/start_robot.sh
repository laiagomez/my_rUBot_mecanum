#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/robot.env"

if [[ ! -f "${CONFIG_FILE}" ]]; then
  echo "Configuration file not found: ${CONFIG_FILE}" >&2
  exit 1
fi

set -a
. "${CONFIG_FILE}"
set +a

source /opt/ros/humble/setup.bash
source "${ROBOT_WORKSPACE}/install/setup.bash"

exec ros2 launch my_robot_bringup my_robot_bringup_robust_hw.launch.py
