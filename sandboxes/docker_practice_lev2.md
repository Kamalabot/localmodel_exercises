## Technology Stack & The Problems They Solve

| Technology | License & Status | What It Is (Usage Intro) | The Layman Problem It Solves |
| --- | --- | --- | --- |
| **Python** | Open-source, Actively developed | A versatile programming language. | "I need a language to quickly write the logic for backend tasks and API endpoints." |
| **FastAPI** | Open-source, Actively developed | A modern, fast web framework for building APIs with Python. | "I need my Python code to stay awake and listen for web requests, routing them to the right functions." |
| **PostgreSQL** | Open-source, Actively developed | A highly stable, relational database. | "I need a permanent, structured vault to store my application's data so it isn't lost on restart." |
| **Valkey** | Open-source (Redis fork), Actively developed | An in-memory data structure store used as a cache. | "My database is getting slammed by identical requests; I need a temporary, lightning-fast memory bank to lighten the load." |
| **Nginx** | Open-source, Actively developed | A high-performance web server and reverse proxy. | "I need a traffic cop to sit in front of my Python app, block bad requests, and serve static files efficiently." |

---

## Module 1: Building Python Images

### Exercise 1: The Single-File Python Container

* **The Layman Problem:** You want to run a Python script on a server without actually installing Python or worrying about version conflicts on the host machine.
* **Goal:** Create a `Dockerfile` that packages a simple script.
* **Task:** Write a Python script (`app.py`) that prints "System Initialized". Write a `Dockerfile` using `python:3.11-slim` as the base, copy the file in, and set the `CMD` to run it.

```bash
docker build -t basic-python-app .
docker run --rm basic-python-app

```

### Exercise 2: Handling Third-Party Dependencies

* **The Layman Problem:** Your script needs external libraries (like `requests`), but you don't want to manually `pip install` them every time you run the app.
* **Goal:** Incorporate a `requirements.txt` into the build process.
* **Task:** Create a script that fetches data from a public API. Add a `requirements.txt`. Update your `Dockerfile` to `COPY requirements.txt .` and `RUN pip install -r requirements.txt` before copying the rest of your code. Build and run it.

### Exercise 3: The Continuous Web Server

* **The Layman Problem:** Scripts run once and die. You need an application that stays alive continuously to listen for incoming web traffic.
* **Goal:** Containerize a FastAPI web server.
* **Task:** Write a basic FastAPI app. In your `Dockerfile`, expose port 8000. Use Uvicorn in your `CMD` to start the server.

```bash
docker build -t my-api .
# Run it, mapping your laptop's port 8080 to the container's 8000
docker run -d -p 8080:8000 --name api-container my-api

```

### Exercise 4: Excluding Junk with `.dockerignore`

* **The Layman Problem:** When Docker builds an image, it copies your whole folder. You are accidentally copying local virtual environments (`.venv`), cached files, and hidden git histories, making the image bloated.
* **Goal:** Keep the build context clean.
* **Task:** Create a `.dockerignore` file. Add `__pycache__`, `.venv`, and `.git`. Rebuild your image and note the faster build time and smaller image size.

### Exercise 5: Multi-Stage Builds for Production

* **The Layman Problem:** You need heavy compiler tools to install some Python packages, but keeping those tools in the final image makes it huge and a security risk.
* **Goal:** Build in one environment, run in another.
* **Task:** Write a multi-stage `Dockerfile`. In `Stage 1`, use a standard Python image to `pip install` dependencies into a specific folder. In `Stage 2`, use a tiny `alpine` or `slim` image, and copy *only* the installed libraries from Stage 1.

---

## Module 2: Environment Variables & Dynamic Config

### Exercise 6: Passing Simple Variables at Runtime

* **The Layman Problem:** You want the same Docker image to connect to a "Testing" database locally, but a "Production" database on the server, without changing the code.
* **Goal:** Use the `-e` flag to inject variables.
* **Task:** Update your Python app to print `os.environ.get("APP_ENV")`. Run the container twice, passing different variables to see the output change.

```bash
docker run --rm -e APP_ENV=Testing my-api
docker run --rm -e APP_ENV=Production my-api

```

### Exercise 7: Bulk Loading with `.env` Files

* **The Layman Problem:** Typing out 15 different API keys and database passwords in the terminal command is insecure and tedious.
* **Goal:** Load variables from a file.
* **Task:** Create a `config.env` file with several dummy variables (e.g., `API_KEY=12345`). Run the container using the `--env-file` flag.

```bash
docker run --rm --env-file config.env my-api

```

### Exercise 8: Dynamic Internal Port Binding

* **The Layman Problem:** You hardcoded your app to listen on port 8000, but the cloud provider you are deploying to requires it to listen on the port they assign dynamically.
* **Goal:** Bind the web server port using an environment variable.
* **Task:** Change your FastAPI startup script to read a `PORT` environment variable. Pass `-e PORT=9000` to the container and map it to your host to verify it shifted successfully.

### Exercise 9: Overriding the Default Command

* **The Layman Problem:** You have one codebase that contains both your web API and a background task worker. You don't want to build two separate images.
* **Goal:** Override the `Dockerfile` CMD at runtime.
* **Task:** Write a `worker.py` script in the same directory. Run your existing API image, but append the command to run the worker instead of the web server at the end of your `docker run` statement.

```bash
docker run --rm my-api python worker.py

```

---

## Module 3: Volumes & Data Binds

### Exercise 10: Rapid Prototyping (Bind Mounts)

* **The Layman Problem:** You are rapidly building a Job Search Agent. Rebuilding the Docker image every time you change a single line of logic slows your development velocity to a crawl.
* **Goal:** Link your host source code directly into the running container.
* **Task:** Start your Python container, using `-v` to map your local code directory over the container's code directory. Edit the Python file on your host machine and watch the FastAPI server reload instantly inside the container.

```bash
docker run -d -p 8080:8000 -v $(pwd):/app my-api

```

### Exercise 11: Named Volumes for Database Permanence

* **The Layman Problem:** You shut down your PostgreSQL container, and all your tables and data vanished.
* **Goal:** Create a Docker-managed storage volume.
* **Task:** Create a volume called `pg_data`. Run a PostgreSQL container and mount this volume to `/var/lib/postgresql/data`. Create a table, destroy the container, start a new one attached to the same volume, and verify the table survived.

```bash
docker volume create pg_data
docker run -d --name my-db -e POSTGRES_PASSWORD=secret -v pg_data:/var/lib/postgresql/data postgres:alpine

```

### Exercise 12: Read-Only Configuration Injection

* **The Layman Problem:** You need to give a container a configuration file from your host, but you want to absolutely guarantee a bug in the container cannot overwrite or delete your local file.
* **Goal:** Use a read-only bind mount.
* **Task:** Create a `settings.json` file on your host. Mount it into a running container using the `:ro` (read-only) flag. Exec into the container and try to edit the file to prove the system blocks you.

### Exercise 13: Database Auto-Initialization

* **The Layman Problem:** You don't want to manually run "CREATE TABLE" commands every time you spin up a fresh local environment.
* **Goal:** Seed the database automatically on its first boot.
* **Task:** Write an `init.sql` file. Use a bind mount to place this file inside the PostgreSQL container's `/docker-entrypoint-initdb.d/` directory. Check the logs to watch Postgres execute it automatically.

---

## Module 4: The Network Layer

### Exercise 14: Creating an Isolated Virtual Network

* **The Layman Problem:** Containers running on the default network can only talk to each other via IP addresses, which change randomly. They need a private network with a built-in DNS (phonebook).
* **Goal:** Create a custom bridge network.
* **Task:** Use the CLI to create a network named `backend-net`.

```bash
docker network create backend-net

```

### Exercise 15: Connecting Python to PostgreSQL

* **The Layman Problem:** Your app needs to securely log into the database without the database being exposed to the public internet.
* **Goal:** Communicate across the custom network using container names.
* **Task:** Attach both your PostgreSQL container and your Python API container to `backend-net`. In your Python code, set the database connection string host to the exact name of the database container (e.g., `postgresql://user:pass@my-db:5432/db`).

### Exercise 16: Resolving Port Conflicts

* **The Layman Problem:** You are running two different web projects on your machine. They both want to use your laptop's port 80, causing a fatal crash.
* **Goal:** Master host port mapping.
* **Task:** Run two identical instances of your API container. Map the first one to host port 8081 (`-p 8081:8000`) and the second one to host port 8082 (`-p 8082:8000`). Verify both are accessible simultaneously.

### Exercise 17: Injecting a Cache Layer

* **The Layman Problem:** Database queries are taking too long. You need a fast, in-memory cache sitting next to the database on the private network.
* **Goal:** Add Valkey to the network topology.
* **Task:** Start a `valkey/valkey:latest` container attached to `backend-net`. Update your Python app to connect to the cache using the container name, temporarily storing data there before falling back to PostgreSQL.

---

## Module 5: Advanced Integration

### Exercise 18: The Ephemeral Migration Container

* **The Layman Problem:** You need to run a script to update the database schema, but this script only needs to run exactly once and then go away. It shouldn't be running constantly like a web server.
* **Goal:** Execute a one-off task on the network.
* **Task:** Package a Python database migration script into an image. Run it with the `--rm` flag and attach it to `backend-net`. Watch it connect, update the database, and immediately delete itself upon completion.

### Exercise 19: The Reverse Proxy

* **The Layman Problem:** Your API is running internally, but you need a highly efficient front-door to handle internet traffic, SSL, and routing before it hits your Python code.
* **Goal:** Route traffic through Nginx.
* **Task:** Create an Nginx container on `backend-net`. Write a custom `nginx.conf` (injected via bind mount) that acts as a `proxy_pass` to route incoming traffic on port 80 to your Python container's internal port 8000.

### Exercise 20: Full Stack Security Validation

* **The Layman Problem:** You need to prove that while the outside world can talk to your Python app, hackers cannot bypass the app and talk directly to your database.
* **Goal:** Verify network isolation boundaries.
* **Task:** Ensure your Nginx container publishes port 80 to your host (`-p 80:80`). Ensure your Python and PostgreSQL containers publish *zero* ports to the host (no `-p` flags). Prove that you can curl the Nginx endpoint successfully, but cannot connect a local database viewer (like DBeaver) directly to the database.