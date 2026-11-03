#!/usr/bin/env bash

set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script with sudo: sudo ./install_robot_udev_rules.sh" >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RULES_SOURCE="${SCRIPT_DIR}/99-rubot-hardware.rules"
RULES_TARGET=/etc/udev/rules.d/99-rubot-hardware.rules
DEVICES=(/dev/robot_arduino /dev/robot_lidar /dev/robot_camera)

if [[ ! -f "${RULES_SOURCE}" ]]; then
  echo "Rules file not found: ${RULES_SOURCE}" >&2
  exit 1
fi

echo "Installing udev rules..."
install -m 0644 "${RULES_SOURCE}" "${RULES_TARGET}"

echo "Reloading udev rules..."
udevadm control --reload-rules
udevadm trigger
udevadm settle --timeout=10

missing=0
echo "Checking stable device names:"
for device in "${DEVICES[@]}"; do
  if [[ -e "${device}" ]]; then
    ls -l "${device}"
  else
    echo "Missing: ${device}" >&2
    missing=1
  fi
done

if [[ "${missing}" -ne 0 ]]; then
  echo "Connect the required hardware and verify its IDs in 3_Install_rubot_robust_bringup_hw.md." >&2
  exit 1
fi

echo "All stable robot device names are available."
