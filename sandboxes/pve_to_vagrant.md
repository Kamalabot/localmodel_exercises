# Engineering Log: Sovereign K3s Cluster Provisioning Roster

## Phase 1: The Proxmox / LXC Bottleneck (The Problem)
* **Context:** Attempted to run K3s worker agents within Linux Containers (LXCs) inside a nested Proxmox virtual environment.
* **The Trap:** Encountered critical container virtualization friction. LXC cgroup restrictions, nested bridging constraints, and lack of direct kernel access caused recurring network deadlocks and blocked TLS handshakes with the control plane (`moship`).
* **The Pivot:** Decoupled entirely from the nested Proxmox environment. Moved the worker nodes directly onto the bare-metal Windows host using VirtualBox for zero-overhead kernel access.

## Phase 2: Hypervisor Control & Automation Setup
* **Tooling Selection:** Deployed **Vagrant** on the Windows host to act as a programmatic remote control for VirtualBox, eliminating manual GUI configuration.
* **Network Infrastructure:** Established a dual-homed network architecture for each agent node:
  * **Interface 1 (NAT):** Hidden interface for outbound WAN access (downloading dependencies/binaries).
  * **Interface 2 (Host-Only):** Locked to the private `192.168.56.x` subnet for secure, direct node-to-master telemetry.

## Phase 3: Vagrant Box & Registry War (The Interventions)
* **The Block:** Standard CLI box downloads (`vagrant up`) failed due to multi-threaded download limits and 21-second timeouts on HashiCorp's AWS S3 acceleration endpoints.
* **Provider Mismatch:** A default cloud fetch accidentally pulled the `libvirt` (Linux-native) box configuration instead of the VirtualBox package, throwing a fatal missing `metadata.json` error.
* **The Fix (Sovereign Injection):** * Manually pulled the official, pristine Debian 12 VirtualBox box archive (`.box`) directly via the web browser to exploit multi-threaded connection handling.
  * Force-injected the local asset into the offline Vagrant registry utilizing explicit provider flags:
    `vagrant box add debian/bookworm64 "D:\sw_to_install\virtual_box\deb_bookworm.box" --provider virtualbox`

## Phase 4: Script Optimization & Asynchronous Provisioning
* **Minimalist OS Fix:** The official Debian cloud image lacked `curl`. Modified the provisioning payload to force non-interactive installations of `curl`, `iptables`, and `iproute2` prior to running the K3s initialization sequence.
* **Synchronous Lockup Fix:** Systemd initially held the SSH TTY session open indefinitely during `systemctl start k3s-agent`. Resolved this by configuring K3s to bypass immediate execution and invoking systemd asynchronously:
  `INSTALL_K3S_SKIP_START=true`
  `sudo systemctl start k3s-agent --no-block`

## Phase 5: Cluster Resource Rebalancing
* **Control Plane Failure:** The incoming TLS telemetry and node registration burst overloaded the master node (`moship`), leading to an HTTP/2 connection drop and API server deadlock (`TLS handshake timeout`).
* **Resolution:** Cleared the deadlocked state, increased the Mothership control plane RAM allocations to 2GB to accommodate the SQLite database cache, and safely downscaled worker node configurations to 1.5GB (1536MB) of RAM inside the `Vagrantfile` loop to optimize overall host allocation.

## Phase 6: Final Verified Cluster State
Executing `kubectl get nodes` on the control plane confirms that all edge agents have securely tunneled through the Host-Only adapter and registered successfully:

```text
NAME           STATUS   ROLES           AGE     VERSION
edge-agent-1   Ready    <none>          31m     v1.35.5+k3s1
edge-agent-2   Ready    <none>          2m25s   v1.35.5+k3s1
edge-agent-3   Ready    <none>          78s     v1.35.5+k3s1
moship         Ready    control-plane   5h44m   v1.35.5+k3s1