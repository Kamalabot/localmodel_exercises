#!/bin/bash

# --- HARD CONTEXT CONFIGS ---
MOTHERSHIP_IP="192.168.56.109"
K3S_TOKEN="token"
BASE_TEMPLATE_ID=299
START_ID=300

print_usage() {
    echo "Usage: $0 [apply|destroy]"
}

if [ "$1" == "apply" ]; then
    echo "=== STARTING FLEET PROVISIONING (DEBIAN 12 SYSTEMD) ==="
    for i in {1..10}; do
        VMID=$((START_ID + i))
        NAME="edge-agent-${i}"
        
        # HIDDEN ROUTER SUBNET
        AGENT_IP="10.56.0.20${i}"
        
        echo "------------------------------------------------------"
        echo "Stamping out ${NAME} (ID: ${VMID}) on IP: ${AGENT_IP}..."
        echo "------------------------------------------------------"
        
        # 1. Clone the pristine Debian 12 baseline
        pct clone ${BASE_TEMPLATE_ID} ${VMID} --hostname ${NAME} --full 0 >/dev/null 2>&1
        
        # 2. Single-NIC Architecture tied to the hidden vmbr2 switch
        pct set ${VMID} --net0 name=eth0,bridge=vmbr2,ip=${AGENT_IP}/24,gw=10.56.0.1
        
        # 3. Fire up the LXC container
        pct start ${VMID}
        
        # Give Debian's systemd 5 seconds to fully initialize the network and services
        sleep 5 
        
        echo "Linking ${NAME} to the Mothership backbone..."
        pct exec ${VMID} -- bash -c "
            # 1. The Proxmox LXC Kubelet Fix
            ln -sf /dev/null /dev/kmsg;
            
            # 2. The MTU Blackhole Fix (Must run before K3s connects)
            ip link set eth0 mtu 1400;
            
            # 3. Define the clean, log-limit-free execution string
            export INSTALL_K3S_EXEC=\"agent --node-ip=${AGENT_IP} --flannel-iface=eth0 --kubelet-arg=cgroups-per-qos=false --kubelet-arg=enforce-node-allocatable=\"
            
            # 4. Native Systemd Install. K3s will automatically create, enable, and start the background service.
            curl -sfL https://get.k3s.io | INSTALL_K3S_SKIP_DOWNLOAD=true K3S_URL=https://${MOTHERSHIP_IP}:6443 K3S_TOKEN=${K3S_TOKEN} sh -s -
        "
        
        # --- THE CANARY CHECKPOINT ---
        if [ "$i" -eq 2 ]; then
            echo ""
            echo "======================================================"
            echo "🛑 CANARY CHECKPOINT REACHED"
            echo "The first 2 Debian agents have been deployed and systemd is running."
            echo "Switch to your Mothership terminal and run: kubectl get nodes"
            echo "Verify they are showing a 'Ready' status before continuing."
            echo "======================================================"
            read -p "Press [ENTER] to deploy the remaining 8 agents, or [CTRL+C] to abort..."
            echo "Resuming fleet deployment..."
        fi
        
    done
    echo "=== FLEET PROVISIONING COMPLETE ==="

elif [ "$1" == "destroy" ]; then
    echo "=== STARTING FLEET DESTRUCTION ==="
    for i in {1..10}; do
        VMID=$((START_ID + i))
        if pct status ${VMID} >/dev/null 2>&1; then
            echo "Stopping and destroying ID: ${VMID}..."
            pct stop ${VMID} --kill 1 >/dev/null 2>&1
            sleep 1
            pct destroy ${VMID} --force 1 >/dev/null 2>&1
        fi
    done
    echo "=== FLEET DESTRUCTION COMPLETE ==="
else
    print_usage
    exit 1
fi