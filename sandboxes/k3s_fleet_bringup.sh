for i in {1..10}; do
    VMID=$((300 + i))
    echo "Activating K3s background process on edge-agent-${i} (ID: ${VMID})..."
    
    # Enable the agent service on system boot inside the LXC
    pct exec ${VMID} -- rc-update add k3s-agent default
    
    # Start the agent service right now
    pct exec ${VMID} -- rc-service k3s-agent start
done