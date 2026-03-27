#!/usr/bin/env bash
set -euo pipefail

AGENTS_SRC_DIR="/Users/wangrenzhu/work/MetaClaw/InfinityCompany/agents"

echo "Registering agents into OpenClaw..."

for agent_dir in "${AGENTS_SRC_DIR}"/*; do
  if [[ -d "$agent_dir" ]]; then
    agent_name=$(basename "$agent_dir")
    
    if [[ "$agent_name" == "caocan" ]]; then
        echo "Skipping caocan (already mapped to main)"
        # ensure identity is up to date for main
        openclaw agents set-identity --agent main --identity-file "${agent_dir}/IDENTITY.md" || true
        continue
    fi
    
    echo "Registering agent: ${agent_name}"
    
    # Check if agent already exists
    if openclaw agents list | grep -q "^- ${agent_name}"; then
        echo "Agent ${agent_name} already exists."
    else
        echo "Creating agent ${agent_name}..."
        openclaw agents add "${agent_name}" --non-interactive --workspace "/Users/wangrenzhu/work/MetaClaw/InfinityCompany" --agent-dir "/Users/wangrenzhu/.openclaw/agents/${agent_name}/agent" || true
    fi
    
    # set identity
    identity_file="${agent_dir}/IDENTITY.md"
    if [[ -f "$identity_file" ]]; then
        echo "Setting identity for ${agent_name}..."
        openclaw agents set-identity --agent "${agent_name}" --identity-file "${identity_file}" || true
    fi
  fi
done

echo "Done registering agents."
