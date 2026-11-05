#!/usr/bin/env bash

set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script with sudo: sudo ./install_local_services.sh" >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/robot.env"
SERVICE_DIR=/etc/systemd/system
SERVICES=(my_robot.service my_rosbridge.service my_robot_web.service)
SCRIPTS=(start_robot.sh start_rosbridge.sh start_web_dashboard.sh)

for file in "${CONFIG_FILE}" "${SERVICES[@]/#/${SCRIPT_DIR}/}" "${SCRIPTS[@]/#/${SCRIPT_DIR}/}"; do
  if [[ ! -f "${file}" ]]; then
    echo "Required file not found: ${file}" >&2
    exit 1
  fi
done

set -a
. "${CONFIG_FILE}"
set +a

if [[ ! -f "${ROBOT_WORKSPACE}/install/setup.bash" ]]; then
  echo "ROS workspace is not built: ${ROBOT_WORKSPACE}/install/setup.bash" >&2
  echo "Run install_ros2_humble_rubot.sh first." >&2
  exit 1
fi

echo "Installing service unit files..."
for service in "${SERVICES[@]}"; do
  install -m 0644 "${SCRIPT_DIR}/${service}" "${SERVICE_DIR}/${service}"
done

echo "Making startup scripts executable..."
for script in "${SCRIPTS[@]}"; do
  chmod 0755 "${SCRIPT_DIR}/${script}"
done

systemctl daemon-reload
systemctl enable --now my_robot.service my_rosbridge.service my_robot_web.service

echo
echo "Services installed. Check their status with:"
echo "  systemctl status my_robot my_rosbridge my_robot_web"
echo "Follow logs with:"
echo "  journalctl -u my_robot -f"
