#!/usr/bin/env bash
set -e

echo "=== 1. Updating System Indexes & Dependencies ==="
sudo apt-get update
sudo apt-get install -y ca-certificates curl

echo "=== 2. Configuring Official Docker Repository ==="
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "=== 3. Installing Open-Source Docker Engine ==="
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "=== 4. Configuring Systemd Units & Exposing TCP Port 2375 ==="
# Strip default systemd runtime execution flags
sudo mkdir -p /etc/systemd/system/docker.service.d
cat << 'EOF' | sudo tee /etc/systemd/system/docker.service.d/override.conf
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd
EOF

# Define sockets (both Unix and network loopback TCP)
sudo mkdir -p /etc/docker
cat << 'EOF' | sudo tee /etc/docker/daemon.json
{
  "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"]
}
EOF

echo "=== 5. Applying Permissions & Group Modifications ==="
# Force create group if missing and append user
sudo groupadd -f docker
sudo usermod -aG docker $USER

# Correct runtime socket permissions explicitly
sudo chown root:docker /var/run/docker.sock 2>/dev/null || true

echo "=== 6. Initializing Docker Engine Daemon ==="
sudo systemctl daemon-reload
sudo systemctl enable docker.service
sudo systemctl restart docker.service

echo "=== 7. Verifying Configuration via Active Subshell ==="
sg docker -c "docker ps"

echo "========================================================="
echo " SETUP COMPLETE!"
echo "========================================================="
echo "To drop into a shell session with active docker access, run:"
echo "  exec sg docker \"\$SHELL\""
echo ""
echo "To connect from Windows PowerShell, run:"
echo "  \$env:DOCKER_HOST=\"tcp://localhost:2375\""
echo "========================================================="