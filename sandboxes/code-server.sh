#!/usr/bin/env bash
set -e

echo "=== 1. Downloading and Installing VS Code Server ==="
curl -fsSL https://code-server.dev/install.sh | sh

echo "=== 2. Creating Configuration Directory Tree ==="
mkdir -p "$HOME/.config/code-server"

echo "=== 3. Injecting Wildcard Network Binding (0.0.0.0:8080) ==="
cat <<EOF > "$HOME/.config/code-server/config.yaml"
bind-addr: 0.0.0.0:8080
auth: none
cert: false
EOF

echo "=== 4. Reloading Systemd Daemons ==="
sudo systemctl daemon-reload

echo "=== 5. Launching User-Instantiated Background Service ==="
sudo systemctl enable --now code-server@$USER

echo "=== 6. Verifying Active Socket Endpoint ==="
sleep 2
ss -tulpn | grep :8080

echo "======================================================="
echo " Complete! Access the IDE via http://<VM_IP_ADDRESS>:8080"
echo " Monitoring state via: sudo systemctl status code-server@$USER"
echo "======================================================="