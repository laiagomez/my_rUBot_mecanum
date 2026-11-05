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

cd "${ROBOT_WORKSPACE}/tools/web_dashboard"
exec /usr/bin/python3 -m http.server "${WEB_PORT}"
