#!/bin/bash
TEMPLATE_ID=299
TARGET_STORAGE="local-lvm"

echo "=== STARTING DEBIAN 12 K3S TEMPLATE BUILD ==="

echo "Updating Proxmox template database..."
pveam update >/dev/null

echo "Downloading the latest Debian 12 standard image..."
pveam download local debian-12-standard >/dev/null 2>&1

RAW_FILE=$(pveam available -section system | grep debian-12-standard | awk '{print $2}' | head -n 1)
TEMPLATE_VOL="local:vztmpl/${RAW_FILE}"

if pct status $TEMPLATE_ID >/dev/null 2>&1; then
    echo "Destroying old template (ID: $TEMPLATE_ID)..."
    pct stop $TEMPLATE_ID 2>/dev/null
    pct destroy $TEMPLATE_ID 2>/dev/null
fi

echo "Stamping out the Debian base container on ${TARGET_STORAGE}..."
pct create $TEMPLATE_ID "${TEMPLATE_VOL}" \
    --storage ${TARGET_STORAGE} \
    --ostype debian \
    --arch amd64 \
    --hostname debian-k3s-base \
    --cores 2 \
    --memory 2048 \
    --swap 0 \
    --unprivileged 1 \
    --net0 name=eth0,bridge=vmbr2,ip=10.56.0.99/24,gw=10.56.0.1 \
    --nameserver 8.8.8.8

echo "Configuring Proxmox LXC features for Kubernetes..."
pct set $TEMPLATE_ID --features nesting=1

echo "Booting container to install K3s prerequisites..."
pct start $TEMPLATE_ID
sleep 5 

echo "Running system updates inside template..."
pct exec $TEMPLATE_ID -- bash -c "apt-get update && apt-get upgrade -y && apt-get install -y curl ca-certificates iptables iproute2 && echo \"en_US.UTF-8 UTF-8\" > /etc/locale.gen && locale-gen"

echo "Baking the K3s binary into the image (Airgap Prep)..."
pct exec $TEMPLATE_ID -- bash -c "curl -sfL https://get.k3s.io | INSTALL_K3S_SKIP_START=true INSTALL_K3S_SKIP_ENABLE=true sh -s -"

echo "Sealing the Debian 12 Template..."
pct stop $TEMPLATE_ID
sleep 2
pct template $TEMPLATE_ID

echo "=== DEBIAN 12 TEMPLATE (ID: $TEMPLATE_ID) IS READY ==="