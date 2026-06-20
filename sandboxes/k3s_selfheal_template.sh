#!/bin/bash

VMID=299

echo "Querying Proxmox mirrors for the latest Alpine template..."
pveam update > /dev/null

# Dynamically extract the newest Alpine template name from the mirror
LATEST_ALPINE=$(pveam available | grep alpine | sort -V | tail -n 1 | awk '{print $2}')

echo "Downloading ${LATEST_ALPINE}..."
pveam download local ${LATEST_ALPINE}

# Format the path for local storage
TEMPLATE="local:vztmpl/${LATEST_ALPINE}"

echo "Building Golden Image (ID: ${VMID})..."

pct create ${VMID} ${TEMPLATE} \
    -storage local-lvm \
    -cores 1 -memory 512 -swap 0 -hostname k3s-golden-base \
    -net0 name=eth0,bridge=vmbr0,ip=dhcp \
    -ostype alpine -unprivileged 0 -features nesting=1 -start 1

cat <<EOF >> /etc/pve/lxc/${VMID}.conf
lxc.apparmor.profile: unconfined
lxc.cgroup2.devices.allow: a
lxc.cap.drop:
lxc.mount.auto: proc:rw sys:rw
EOF

# Restart to apply kernel nestings
pct stop ${VMID} && pct start ${VMID}
sleep 5

echo "Pre-loading dependencies and K3s binary (Skipping Start)..."

pct exec ${VMID} -- ash -c "
    apk update;
    apk add --no-cache curl bash coreutils findutils util-linux mount iptables logrotate;
    
    echo '/var/log/k3s.log { size 10M rotate 2 copytruncate missingok }' > /etc/logrotate.d/k3s;
    echo '*/15 * * * * logrotate /etc/logrotate.d/k3s' >> /etc/crontabs/root;
    
    rc-update add cgroups default;
    
    # Download K3s but strictly forbid it from generating keys or starting
    curl -sfL https://get.k3s.io | INSTALL_K3S_SKIP_START=true INSTALL_K3S_SKIP_ENABLE=true sh -
"

echo "Locking into Proxmox Template..."
pct stop ${VMID}
pct template ${VMID}
echo "Golden Image locked and ready for cloning."