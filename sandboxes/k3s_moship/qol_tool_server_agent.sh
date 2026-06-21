#!/bin/sh
# qol-bootstrap.sh
# Purpose: Unified injection of sovereign QOL tooling into the K3s control plane.

set -e

echo "[INFO] Commencing Unified QOL Tool Injection..."

# 1. Install k9s
echo "[INFO] Fetching k9s terminal UI..."
curl -sS https://webinstall.dev/k9s | sh
export PATH="/root/.local/bin:$PATH"
echo "export PATH=\"/root/.local/bin:\$PATH\"" >> ~/.profile

# 2. Install Kubeshark
echo "[INFO] Fetching Kubeshark API Analyzer..."
curl -Lo kubeshark https://github.com/kubeshark/kubeshark/releases/latest/download/kubeshark_linux_amd64
chmod 755 kubeshark
mv kubeshark /usr/local/bin/

# 3. Install Helmfile (Assumes Helm is already installed from Phase 1)
echo "[INFO] Fetching Helmfile orchestrator..."
curl -Lo helmfile https://github.com/helmfile/helmfile/releases/latest/download/helmfile_linux_amd64
chmod +x helmfile
mv helmfile /usr/local/bin/

echo "[SUCCESS] Sovereign QOL Stack is active."
echo "-> Type 'k9s' to enter the visual cluster terminal."
echo "-> Type 'kubeshark tap' to begin intercepting pod traffic."