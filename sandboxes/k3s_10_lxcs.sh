#!/bin/bash

# --- CONFIGURATION TARGETS ---
MOTHERSHIP_IP="192.168.56.109"
K3S_TOKEN="YOUR_EXTRACTED_NODE_TOKEN_HERE"
START_ID=300

# 1. Ensure the local Alpine LXC template exists (~5MB download)
pveam update
TEMPLATE=$(pveam list local | grep alpine | head -n 1 | awk '{print $2}')
if [ -z "$TEMPLATE" ]; then
    echo "Downloading ultra-lightweight Alpine LXC template..."
    pveam download local alpine-3.19-default_20240206_amd64.tar.zst
    TEMPLATE="local:vztmpl/alpine-3.19-default_20240206_amd64.tar.zst"
fi

# 2. Deploy and orchestrate the 10 Edge Agents
for i in {1..10}; do
    VMID=$((START_ID + i))
    NAME="edge-agent-${i}"
    
    # Assign a static IP for the private cluster backbone to guarantee stability
    AGENT_IP="192.168.56.20${i}"
    
    echo "------------------------------------------------------"
    echo "Building ${NAME} (ID: ${VMID}) on IP: ${AGENT_IP}..."
    echo "------------------------------------------------------"
    
    # Provision with Dual NICs: net0 (Internet) and net1 (Cluster Backbone)
    pct create ${VMID} ${TEMPLATE} \
        -cores 1 \
        -memory 512 \
        -swap 0 \
        -hostname ${NAME} \
        -net0 name=eth0,bridge=vmbr0,ip=dhcp \
        -net1 name=eth1,bridge=vmbr1,ip=${AGENT_IP}/24 \
        -ostype alpine \
        -unprivileged 0 \
        -features nesting=1 \
        -start 1
        
    # Inject kernel bypasses for container nesting
    cat <<EOF >> /etc/pve/lxc/${VMID}.conf
lxc.apparmor.profile: unconfined
lxc.cgroup2.devices.allow: a
lxc.cap.drop:
lxc.mount.auto: proc:rw sys:rw
EOF

    # Allow network interfaces to pull DHCP and settle
    sleep 5
    
    echo "Bootstrapping K3s Agent and Log Policies inside ${NAME}..."
    
    # Execute the internal setup, log restrictions, and K3s agent binding
    pct exec ${VMID} -- ash -c "
        apk update;
        apk add --no-cache curl bash coreutils findutils util-linux mount iptables logrotate;
        
        # SPACE & LOG MANAGEMENT: Prevent /var/log/k3s.log from filling the LXC disk
        echo '/var/log/k3s.log { size 10M rotate 2 copytruncate missingok }' > /etc/logrotate.d/k3s;
        echo '*/15 * * * * logrotate /etc/logrotate.d/k3s' >> /etc/crontabs/root;
        crond;
        
        # Initialize kernel control groups
        rc-update add cgroups default;
        rc-service cgroups start;
        mount --make-rshared /;
        
        # Launch K3s Agent: Bind specifically to eth1 and limit pod log sizes
        curl -sfL https://get.k3s.io | K3S_URL=https://${MOTHERSHIP_IP}:6443 K3S_TOKEN=${K3S_TOKEN} sh -s - agent --node-ip=${AGENT_IP} --flannel-iface=eth1 --container-log-max-size=10Mi --container-log-max-files=2
    "
    
    echo "--> ${NAME} successfully deployed."
done