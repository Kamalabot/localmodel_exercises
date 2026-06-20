#!/bin/bash

MOTHERSHIP_IP="192.168.56.109"
K3S_TOKEN="token"
BASE_TEMPLATE_ID=299
START_ID=300

print_usage() {
    echo "Usage: $0 [apply|destroy]"
}

if [ "$1" == "apply" ]; then
    echo "=== STARTING FLEET PROVISIONING ==="
    for i in {1..10}; do
        VMID=$((START_ID + i))
        NAME="edge-agent-${i}"
        AGENT_IP="10.56.0.20${i}"
        
        echo "------------------------------------------------------"
        echo "Stamping out ${NAME} (ID: ${VMID}) on IP: ${AGENT_IP}..."
        echo "------------------------------------------------------"
        
        pct clone ${BASE_TEMPLATE_ID} ${VMID} --hostname ${NAME} --full 0 >/dev/null 2>&1
        pct set ${VMID} --net0 name=eth0,bridge=vmbr2,ip=${AGENT_IP}/24,gw=10.56.0.1
        pct start ${VMID}
        sleep 2
        
        echo "Linking ${NAME} to the Mothership backbone..."
        pct exec ${VMID} -- ash -c "
            rc-service cgroups start 2>/dev/null;
            mount --make-rshared /;
            ln -sf /dev/null /dev/kmsg;
	    
            # The MTU Blackhole Fix
            ip link set eth0 mtu 1400;
            
            # Pass arguments via ENV to prevent OpenRC quote mangling
            export INSTALL_K3S_EXEC=\"agent --node-ip=${AGENT_IP} --flannel-iface=eth0 --kubelet-arg=cgroups-per-qos=false --kubelet-arg=enforce-node-allocatable=\"
            
            # The installer automatically registers and starts the daemon
            curl -sfL https://get.k3s.io | INSTALL_K3S_SKIP_DOWNLOAD=true K3S_URL=https://${MOTHERSHIP_IP}:6443 K3S_TOKEN=${K3S_TOKEN} sh -s -
        "
        
        if [ "$i" -eq 2 ]; then
            echo ""
            echo "======================================================"
            echo "🛑 CANARY CHECKPOINT REACHED"
            echo "Switch to your Mothership terminal and run: kubectl get nodes"
            echo "Verify they are showing a 'Ready' status before continuing."
            echo "======================================================"
            read -p "Press [ENTER] to deploy the remaining 8 agents, or [CTRL+C] to abort..."
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