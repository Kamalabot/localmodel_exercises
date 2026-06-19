## Technology Stack & The Problems They Solve

| Technology | License & Status | What It Is (Usage Intro) | The Layman Problem It Solves |
| --- | --- | --- | --- |
| **Prometheus** | Open-source, Actively developed | A time-series database and scraping engine. | "I need a central brain that asks all my servers 'How are you feeling?' every 5 seconds and records the answers." |
| **Grafana** | Open-source (AGPL), Actively developed | A data visualization platform. | "Staring at endless rows of numbers is impossible; I need beautiful, real-time line charts and warning lights." |
| **Node Exporter** | Open-source, Actively developed | A lightweight hardware sensor. | "I need a tool that specifically measures CPU temperature, disk space, and RAM usage on the physical or virtual hardware." |
| **cAdvisor** | Open-source, Actively developed | A container-specific metric collector. | "I know the whole server's RAM usage, but I need to know exactly which specific Docker container is hogging it all." |
| **Loki & Promtail** | Open-source, Actively developed | A log aggregation system (Loki) and its shipping agent (Promtail). | "I have 20 containers writing error logs; I cannot check them one by one. I need all text logs streamed into one searchable search bar." |

---

### Module 1: Deploying the Sensors (Full Steps)

*This module places the data-gathering agents across your physical host, virtual host, and container engine.*

#### Exercise 1: The Main Host Sensor (Your Physical Laptop)

* **The Layman Problem:** We want our central monitoring system (running inside the VM) to be able to monitor the physical laptop it is living on.
* **Goal:** Run Node Exporter natively on your physical machine.
* **Full Steps:**
1. Download the Node Exporter binary for your physical OS (Windows, macOS, or Linux) from the Prometheus releases page.
2. Extract it and run it directly in your physical machine's terminal:
```bash
./node_exporter

```


3. Open a browser on your physical machine and go to `http://localhost:9100/metrics`. You will see a wall of text (metrics).
4. **The Network Bridge:** Note that from inside your VirtualBox NAT network, your physical host is always accessible at IP `10.0.2.2`. Keep this process running.



#### Exercise 2: The VBox Guest Sensor (Ubuntu VM)

* **The Layman Problem:** We need to measure the virtual hardware (the slice of RAM and CPU we assigned to the VM).
* **Goal:** Run Node Exporter as a background system service inside the VirtualBox Ubuntu machine.
* **Full Steps:**
1. SSH into your VBox Ubuntu machine.
2. Use Docker to run Node Exporter directly attached to the host network so it reads the VM's hardware, not the container's isolated hardware:
```bash
docker run -d \
  --net="host" \
  --pid="host" \
  -v "/:/rootfs:ro" \
  --path.rootfs=/rootfs \
  --name vbox_node_exporter \
  quay.io/prometheus/node-exporter:latest

```


3. Run `curl http://localhost:9100/metrics` inside the VM to verify it is collecting data.



#### Exercise 3: Exposing the Docker Daemon

* **The Layman Problem:** The Docker engine itself knows how many containers are running, paused, or crashed, but it keeps that information secret by default.
* **Goal:** Reconfigure the Docker Engine inside your VBox to broadcast its internal metrics.
* **Full Steps:**
1. SSH into your VBox machine. Create or edit the Docker daemon configuration file:
```bash
sudo nano /etc/docker/daemon.json

```


2. Add the configuration to expose metrics on port 9323:
```json
{
  "metrics-addr": "0.0.0.0:9323"
}

```


3. Restart the Docker service to apply changes:
```bash
sudo systemctl restart docker

```


4. Verify it works: `curl http://localhost:9323/metrics`.



#### Exercise 4: Container X-Ray Vision (cAdvisor)

* **The Layman Problem:** We need granular data on every running container (e.g., Container A is using 50MB of RAM, Container B is using 2GB).
* **Goal:** Deploy cAdvisor, giving it deep kernel access to monitor container control groups (cgroups).
* **Full Steps:**
1. Run the cAdvisor container inside your VBox VM, mounting the highly sensitive system directories it needs to inspect the host:
```bash
docker run -d \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --volume=/dev/disk/:/dev/disk:ro \
  --publish=8080:8080 \
  --name=cadvisor \
  --privileged \
  --device=/dev/kmsg \
  gcr.io/cadvisor/cadvisor:latest

```


2. Open your host machine's browser and navigate to `http://localhost:8080` (assuming you port-forwarded 8080 from VBox in earlier lessons).



---

### Module 2: The Central Brain & Dashboards (Full Steps)

*This module collects the data from Module 1 and visualizes it.*

#### Exercise 5: Wiring the Prometheus Brain

* **The Layman Problem:** The sensors are broadcasting data, but nobody is recording it. We need a system to scrape them all simultaneously.
* **Goal:** Deploy Prometheus using a configuration file that targets the Main Host, the VBox Guest, the Docker Daemon, and cAdvisor.
* **Full Steps:**
1. Inside your VBox VM, create a configuration file named `prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'main_host_laptop'
    static_configs:
      - targets: ['10.0.2.2:9100'] # VirtualBox NAT gateway to host

  - job_name: 'vbox_guest_os'
    static_configs:
      - targets: ['172.17.0.1:9100'] # Docker's default bridge IP to VM host

  - job_name: 'docker_daemon'
    static_configs:
      - targets: ['172.17.0.1:9323']

  - job_name: 'cadvisor_containers'
    static_configs:
      - targets: ['172.17.0.1:8080']

```


2. Deploy Prometheus attached to this file:
```bash
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

```





#### Exercise 6: Launching the Visualization Layer (Grafana)

* **The Layman Problem:** Prometheus data is just raw numbers in a database. We need a graphical dashboard to make sense of it.
* **Goal:** Run Grafana and connect it to Prometheus.
* **Full Steps:**
1. Deploy Grafana inside the VM:
```bash
docker run -d --name grafana -p 3000:3000 grafana/grafana-enterprise

```


2. Open `http://localhost:3000` (forwarded to your host). Log in with `admin` / `admin`.
3. Navigate to **Connections -> Data Sources -> Add data source**.
4. Select **Prometheus**. In the URL field, enter `http://172.17.0.1:9090`. Click **Save & Test**.



#### Exercise 7: Visualizing the VirtualBox & Host OS

* **The Layman Problem:** Building dashboards from scratch takes hours. We want to leverage the open-source community's pre-built designs.
* **Goal:** Import a comprehensive dashboard for Node Exporter.
* **Full Steps:**
1. In Grafana, click the **+ (Plus)** icon in the top right -> **Import dashboard**.
2. Type the community ID `1860` (Node Exporter Full) into the "Import via grafana.com" field and click Load.
3. Select your Prometheus data source from the dropdown at the bottom.
4. Click Import. You will instantly see a professional dashboard showing CPU, RAM, and disk metrics. Look at the "Job" dropdown at the top to switch between your `main_host_laptop` and `vbox_guest_os`.



#### Exercise 8: Visualizing Container Dynamics

* **The Layman Problem:** We need to see exactly how much RAM and CPU our Docker containers are consuming in real-time.
* **Goal:** Import a cAdvisor dashboard to monitor container health.
* **Full Steps:**
1. In Grafana, go to **Import dashboard** again.
2. Type the ID `14282` (cAdvisor Exporter) or `193` (Docker monitoring) and click Load.
3. Select your Prometheus data source.
4. Click Import. You can now track exact resource utilization per container, allowing you to catch memory leaks in your Python code from previous exercises.



---

### Module 3: Log Aggregation (Concepts & Execution)

#### Exercise 9: Deploying the Loki Database

* **Goal:** Run Grafana Loki (the database for logs).
* **Task:** Use Docker to spin up a single-node Loki instance on port 3100. Add it to Grafana as a new Data Source, just like you did with Prometheus.

#### Exercise 10: The Docker Loki Logging Driver

* **Goal:** Stop Docker from saving text logs to hidden local files and stream them directly over the network to Loki.
* **Task:** Install the Docker Loki plugin (`docker plugin install loki`). Edit your `daemon.json` to set `loki` as the default `log-driver`, pushing logs to `http://localhost:3100/loki/api/v1/push`. Restart the Docker service.

#### Exercise 11: Promtail for Host Syslogs

* **Goal:** Capture the operating system's internal logs (like SSH login attempts) from the VBox machine.
* **Task:** Deploy Promtail via Docker. Use a bind mount to map `/var/log` from the VBox host into the Promtail container, and configure Promtail to forward those logs to Loki.

#### Exercise 12: Exploring Logs in Grafana

* **Goal:** Learn how to query logs using LogQL (Loki Query Language).
* **Task:** Go to the "Explore" tab in Grafana. Select Loki. Write a query like `{container_name="cadvisor"}` to see live streaming text logs from that specific system.

---

### Module 4: Active Monitoring & Alerting

#### Exercise 13: Defining Alerting Rules

* **Goal:** Teach Prometheus what a "bad" state looks like.
* **Task:** Create an `alerts.yml` file. Write a PromQL rule that triggers if `node_memory_MemAvailable_bytes` drops below 10% for more than 1 minute. Mount this file into your Prometheus container.

#### Exercise 14: Docker Native Healthchecks

* **Goal:** Tell the Docker engine how to test if an application is actually working, not just "running".
* **Task:** Take the Python FastAPI container from the previous module. Add a `HEALTHCHECK` instruction to the Dockerfile that runs a `curl -f http://localhost:8000/health` every 10 seconds. Observe its status change from "starting" to "healthy" using `docker ps`.

#### Exercise 15: Chaos Observability

* **Goal:** Prove your monitoring system works by intentionally breaking the environment.
* **Task:** Run a container that executes a continuous loop (`while true; do true; done`) to spike the CPU to 100%. Watch your Grafana dashboard light up red, verify the CPU spike is tracked to that specific container via cAdvisor, and observe the Prometheus alerts trigger. Kill the container and watch the system recover.