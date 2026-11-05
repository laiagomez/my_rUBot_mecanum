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

exec ros2 run rosbridge_server rosbridge_websocket \
  --port "${ROSBRIDGE_PORT}" \
  --address 0.0.0.0 \
  --ros-args \
  -p default_call_service_timeout:=5.0 \
  -p call_services_in_new_thread:=true \
  -p send_action_goals_in_new_thread:=true
