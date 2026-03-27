#!/usr/bin/env bash
set -euo pipefail

target_uri="${1:-viking://agent/memories}"

openclaw config set plugins.entries.openviking.enabled true
openclaw config set plugins.slots.memory openviking
openclaw config set plugins.slots.contextEngine openviking
openclaw config set plugins.entries.openviking.config.targetUri "$target_uri"
openclaw gateway restart
openclaw config get plugins.entries.openviking.config.targetUri
