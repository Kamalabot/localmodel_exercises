* **Docker Container:** A single, isolated Linux process. It has its own private filesystem and network interface. It maps strictly **1:1** with an application component.
* **Kubernetes Pod:** A wrapper that holds **one or more** containers.

### The Key Differences

* **The Unit of Scale:** Docker manages containers. Kubernetes only manages Pods. You cannot run a naked container inside Kubernetes; it must be wrapped inside a Pod.
* **Shared Resources:** All containers inside a single Pod share the **exact same** Network Namespace (`localhost`), storage volumes, and IP address. They act like tightly coupled applications running on the same local server.
* **The Use Case:** Most Pods contain just a single container. However, you use a multi-container Pod when you want an auxiliary container (like a log-shipper or proxy) to sit right next to your main application container.

They spin up your services on **completely separate, individual pods** distributed across your nodes.

Because your `cluster-topology.yaml` defines three distinct `Deployments` (`state-db`, `custom-backend`, and `custom-frontend`), K3s treats them as entirely isolated application lifecycles.

Here is exactly how the cluster schedules and separates them:

### 1. Isolated Deployment Pods (Default Architecture)

The Moship reads your three separate tiers and instructs the agents to spin up independent pods for each service. They do **not** merge into the same pod:

* **`state-db` Pod:** Runs a single container (`redis:7-alpine`).
* **`custom-backend` Pods:** Run two isolated pods across the fleet, each holding a `python:3.11-alpine` container running your `main.py`.
* **`custom-frontend` Pods:** Run two isolated pods across the fleet, each holding an `nginx:alpine` container running your proxy routing rules.

Because they are in separate pods, they get distinct internal cluster IP addresses. They talk to each other over your virtual host-only network using the Kubernetes internal DNS services (`state-db-svc` and `backend-api-svc`) that you established.

### 2. When would you put them in the *same* Pod?

You *could* technically force your Python backend and Nginx frontend to run inside the exact same pod wrapper (sharing `localhost`), but you almost never want to do this for core services.

You only combine multiple containers into a single pod when they are tightly coupled dependencies that **must live and die together**—such as a main application container paired with a "Sidecar" container (e.g., a local database log-shipper, a secure service-mesh proxy, or a local credential rotator).

Since your frontend, backend, and database need to scale independently, K3s keeps them isolated on individual pods across your Vagrant fleet.

kubectl delete node edge-agent

kubectl -n kube-system delete secret edge-agent.node-password.k3s --ignore-not-found