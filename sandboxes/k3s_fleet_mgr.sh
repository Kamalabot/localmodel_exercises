#!/bin/bash

# --- CONFIGURATION TARGETS ---
MOTHERSHIP_IP="192.168.56.109"
K3S_TOKEN="token"
BASE_TEMPLATE_ID=299
START_ID=300

print_usage() {
    echo "Usage: $0 [apply|destroy]"
    echo "  apply   - Instantly stamp out and attach the 10 edge agents"
    echo "  destroy - Cleanly purge all 10 edge agents from Proxmox"
}

if [ "$1" == "apply" ]; then
    echo "=== STARTING FLEET PROVISIONING ==="
    for i in {1..10}; do
        VMID=$((START_ID + i))
        NAME="edge-agent-${i}"
        AGENT_IP="192.168.56.20${i}"
        
        echo "Stamping out ${NAME} (ID: ${VMID}) on IP: ${AGENT_IP}..."
        
        # Linked clone from our local template
        pct clone ${BASE_TEMPLATE_ID} ${VMID} --hostname ${NAME} --full 0
        
        # Configure the dual-network sockets
        pct set ${VMID} --net0 name=eth0,bridge=vmbr0,ip=dhcp
        pct set ${VMID} --net1 name=eth1,bridge=vmbr1,ip=${AGENT_IP}/24
        
        # Spin up the container
        pct start ${VMID}
        sleep 2
        
        echo "Linking ${NAME} to the Mothership backbone..."
        pct exec ${VMID} -- ash -c "
            rc-service cgroups start 2>/dev/null;
            mount --make-rshared /;
            
            # Register the background OpenRC service configurations
            rc-update add k3s-agent default 2>/dev/null;
            
            # Run the installer mapping directly to the configured OpenRC daemon environment
            curl -sfL https://get.k3s.io | INSTALL_K3S_SKIP_DOWNLOAD=true K3S_URL=https://${MOTHERSHIP_IP}:6443 K3S_TOKEN=${K3S_TOKEN} sh -s - agent --node-ip=${AGENT_IP} --flannel-iface=eth1 --container-log-max-size=10Mi --container-log-max-files=2;
            
            # Explicitly force-start the background engine daemon immediately
            rc-service k3s-agent start
        "
    done
    echo "=== FLEET PROVISIONING COMPLETE ==="

elif [ "$1" == "destroy" ]; then
    echo "=== STARTING FLEET DESTRUCTION ==="
    for i in {1..10}; do
        VMID=$((START_ID + i))
        NAME="edge-agent-${i}"
        
        if pct status ${VMID} >/dev/null 2>&1; then
            echo "Stopping and destroying ${NAME} (ID: ${VMID})..."
            # Force immediate kill to prevent asynchronous lockouts
            pct stop ${VMID} --kill 1 >/dev/null 2>&1
            sleep 1
            pct destroy ${VMID} --force 1 >/dev/null 2>&1
            echo "--> ${NAME} cleanly purged."
        else
            echo "--> ${NAME} (ID: ${VMID}) does not exist. Skipping."
        fi
    done
    echo "=== FLEET DESTRUCTION COMPLETE ==="

else
    print_usage
    exit 1
fi