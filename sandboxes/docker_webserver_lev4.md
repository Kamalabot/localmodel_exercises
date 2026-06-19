## Technology Stack & The Problems They Solve

| Technology | License & Status | What It Is (Usage Intro) | The Layman Problem It Solves |
| --- | --- | --- | --- |
| **Nginx** | Open-source, Actively developed | A highly efficient, event-driven web server and reverse proxy. | "I need a lightweight receptionist that can handle 10,000 visitors at once, quickly handing them static files or pointing them to the right backend." |
| **Apache HTTP Server** | Open-source, Actively developed | A robust, highly configurable web server reliant on a module system. | "I have a massive application where individual folders need to dictate their own complex security and routing rules without restarting the server." |
| **Caddy** | Open-source, Actively developed | A modern web server written in Go that manages TLS certificates automatically. | "I want to serve a website securely over HTTPS instantly, without spending hours manually requesting and installing SSL certificates." |
| **Traefik/Whoami** | Open-source, Actively developed | A tiny Go web server that prints OS information and HTTP requests. | "I need a dummy backend application to prove my web server is successfully routing traffic." |

---

## The 10 Web Server Exercises

*Note: Run these commands in the environment where your Docker Engine lives (e.g., your VBox Ubuntu machine). The verification steps assume you are testing from your physical host laptop. Ensure your VBox is port-forwarding the 8000-range ports to your physical host, or access the VM's NAT IP directly if configured.*

### Part 1: Nginx (The High-Performance Workhorse)

#### Exercise 1: Serving Static Assets (The Foundation)

* **The Layman Problem:** You have raw HTML and CSS files, but double-clicking them in a browser doesn't mimic a real server environment.
* **Goal:** Use Nginx to serve local files over HTTP.
* **Steps:**

```bash
# 1. Create the content on your host
mkdir -p ~/web-lab/nginx-static
echo "<h1>Hello from Nginx Static</h1>" > ~/web-lab/nginx-static/index.html

# 2. Run Nginx, mapping the folder to the default Nginx HTML path
docker run -d --name nginx_static -p 8081:80 -v ~/web-lab/nginx-static:/usr/share/nginx/html nginx:alpine

```

* **Host Verification:** Open your laptop's browser and go to `http://localhost:8081`.

#### Exercise 2: The Reverse Proxy

* **The Layman Problem:** You have a Python API running internally on port 8000, but users should only connect to standard port 80. You need a middleman.
* **Goal:** Configure Nginx to proxy traffic to a dummy backend.
* **Steps:**

```bash
# 1. Start a dummy backend application
docker run -d --name backend_api -p 8000:80 traefik/whoami

# 2. Create an Nginx config file
mkdir -p ~/web-lab/nginx-proxy
cat <<EOF > ~/web-lab/nginx-proxy/default.conf
server {
    listen 80;
    location / {
        proxy_pass http://host.docker.internal:8000;
        proxy_set_header Host \$host;
    }
}
EOF

# 3. Run Nginx with the custom config
docker run -d --name nginx_proxy -p 8082:80 \
  --add-host host.docker.internal:host-gateway \
  -v ~/web-lab/nginx-proxy/default.conf:/etc/nginx/conf.d/default.conf nginx:alpine

```

* **Host Verification:** Open `http://localhost:8082`. You will see the plain-text output from the dummy backend.

#### Exercise 3: Round-Robin Load Balancing

* **The Layman Problem:** One backend server cannot handle the traffic. You need Nginx to distribute requests equally across three identical servers.
* **Goal:** Implement an Nginx upstream block.
* **Steps:**

```bash
# 1. Start three dummy backends
docker run -d --name worker1 traefik/whoami
docker run -d --name worker2 traefik/whoami
docker run -d --name worker3 traefik/whoami

# 2. Create the load balancer config
mkdir -p ~/web-lab/nginx-lb
cat <<EOF > ~/web-lab/nginx-lb/nginx.conf
events {}
http {
    upstream my_app {
        server worker1;
        server worker2;
        server worker3;
    }
    server {
        listen 80;
        location / {
            proxy_pass http://my_app;
        }
    }
}
EOF

# 3. Create a bridge network and connect everything
docker network create lb-net
docker network connect lb-net worker1
docker network connect lb-net worker2
docker network connect lb-net worker3

# 4. Run the Nginx Load Balancer
docker run -d --name nginx_lb -p 8083:80 --net lb-net \
  -v ~/web-lab/nginx-lb/nginx.conf:/etc/nginx/nginx.conf nginx:alpine

```

* **Host Verification:** Refresh `http://localhost:8083` multiple times. Notice the "Hostname" field in the output changes as Nginx cycles through the three workers.

---

### Part 2: Apache HTTP Server (The Legacy Powerhouse)

#### Exercise 4: Directory Browsing

* **The Layman Problem:** You want to share a folder of files (like an FTP server) via a web browser, but Apache blocks directory listing by default for security.
* **Goal:** Enable the `Options +Indexes` directive via an `.htaccess` file.
* **Steps:**

```bash
# 1. Create a folder with dummy files
mkdir -p ~/web-lab/apache-files
echo "Secret data" > ~/web-lab/apache-files/file1.txt
echo "More data" > ~/web-lab/apache-files/file2.txt

# 2. Create the .htaccess file to allow indexing
echo "Options +Indexes" > ~/web-lab/apache-files/.htaccess

# 3. Run Apache (httpd)
docker run -d --name apache_indexes -p 8084:80 -v ~/web-lab/apache-files:/usr/local/apache2/htdocs/ httpd:alpine

```

* **Host Verification:** Open `http://localhost:8084`. You will see a clickable file directory instead of a default web page.

#### Exercise 5: URL Rewriting (`mod_rewrite`)

* **The Layman Problem:** You renamed an old webpage from `old-page.html` to `new-page.html`. You need the server to automatically redirect users who have the old link bookmarked.
* **Goal:** Use Apache's rewrite engine to manage redirects.
* **Steps:**

```bash
# 1. Setup the workspace
mkdir -p ~/web-lab/apache-rewrite
echo "<h1>Welcome to the New Page</h1>" > ~/web-lab/apache-rewrite/new-page.html

# 2. Extract default Apache config, enable mod_rewrite, and inject rule
docker run --rm httpd:alpine cat /usr/local/apache2/conf/httpd.conf > ~/web-lab/apache-rewrite/httpd.conf
sed -i 's/#LoadModule rewrite_module/LoadModule rewrite_module/g' ~/web-lab/apache-rewrite/httpd.conf

# Add the rewrite rule to the bottom of the config
cat <<EOF >> ~/web-lab/apache-rewrite/httpd.conf
<VirtualHost *:80>
    DocumentRoot "/usr/local/apache2/htdocs"
    RewriteEngine On
    RewriteRule ^/old-page\.html$ /new-page.html [R=301,L]
</VirtualHost>
EOF

# 3. Run Apache
docker run -d --name apache_rewrite -p 8085:80 \
  -v ~/web-lab/apache-rewrite/httpd.conf:/usr/local/apache2/conf/httpd.conf \
  -v ~/web-lab/apache-rewrite:/usr/local/apache2/htdocs/ httpd:alpine

```

* **Host Verification:** Navigate to `http://localhost:8085/old-page.html`. Your browser will automatically redirect to `/new-page.html`.

#### Exercise 6: Password Protection (Basic Auth)

* **The Layman Problem:** You have a private dashboard folder that should prompt users for a username and password before loading.
* **Goal:** Secure a directory using Apache `htpasswd`.
* **Steps:**

```bash
# 1. Setup workspace
mkdir -p ~/web-lab/apache-auth
echo "<h1>Top Secret</h1>" > ~/web-lab/apache-auth/index.html

# 2. Generate a password file (Username: admin, Password: password123)
docker run --rm xmartlabs/htpasswd admin password123 > ~/web-lab/apache-auth/.htpasswd

# 3. Create .htaccess to enforce auth
cat <<EOF > ~/web-lab/apache-auth/.htaccess
AuthType Basic
AuthName "Restricted Area"
AuthUserFile /usr/local/apache2/htdocs/.htpasswd
Require valid-user
EOF

# 4. Modify httpd.conf to allow .htaccess overrides
docker run --rm httpd:alpine cat /usr/local/apache2/conf/httpd.conf > ~/web-lab/apache-auth/httpd.conf
sed -i 's/AllowOverride None/AllowOverride All/g' ~/web-lab/apache-auth/httpd.conf

# 5. Run Apache
docker run -d --name apache_auth -p 8086:80 \
  -v ~/web-lab/apache-auth/httpd.conf:/usr/local/apache2/conf/httpd.conf \
  -v ~/web-lab/apache-auth:/usr/local/apache2/htdocs/ httpd:alpine

```

* **Host Verification:** Go to `http://localhost:8086`. A native browser prompt will ask for credentials.

---

### Part 3: Caddy (The Modern Edge)

#### Exercise 7: Automatic Local HTTPS

* **The Layman Problem:** Browsers throw "Not Secure" warnings on local development environments, preventing testing of secure cookies or web APIs.
* **Goal:** Use Caddy to automatically generate a self-signed local SSL certificate.
* **Steps:**

```bash
mkdir -p ~/web-lab/caddy-tls
echo "<h1>Secure Localhost</h1>" > ~/web-lab/caddy-tls/index.html

cat <<EOF > ~/web-lab/caddy-tls/Caddyfile
localhost {
    tls internal
    file_server
}
EOF

docker run -d --name caddy_tls -p 8087:80 -p 8443:443 \
  -v ~/web-lab/caddy-tls/Caddyfile:/etc/caddy/Caddyfile \
  -v ~/web-lab/caddy-tls:/srv caddy:alpine

```

* **Host Verification:** Open `https://localhost:8443` (Note the `https`). Your browser will warn you the cert is self-signed (since it's not verified by a public authority), but bypass the warning to see encrypted local traffic.

#### Exercise 8: The One-Liner Reverse Proxy

* **The Layman Problem:** Configuring Nginx reverse proxies requires 10 lines of boilerplate text. Caddy aims to do it in one.
* **Goal:** Proxy traffic to a backend using Caddy's simplified syntax.
* **Steps:**

```bash
# 1. Start backend
docker run -d --name caddy_backend -p 8001:80 traefik/whoami

# 2. Run Caddy explicitly from the CLI without a config file
docker run -d --name caddy_proxy -p 8088:80 \
  --add-host host.docker.internal:host-gateway \
  caddy:alpine caddy reverse-proxy --from :80 --to host.docker.internal:8001

```

* **Host Verification:** Go to `http://localhost:8088`. You will see the backend output, configured entirely via a single terminal command.

#### Exercise 9: Path-Based Routing (API Gateway)

* **The Layman Problem:** You have two separate apps (a UI and an API). You want `example.com/` to go to the UI, and `example.com/api/` to go to the API.
* **Goal:** Build an API gateway with Caddy.
* **Steps:**

```bash
mkdir -p ~/web-lab/caddy-routes
echo "<h1>Frontend UI</h1>" > ~/web-lab/caddy-routes/index.html

# Start the API backend
docker run -d --name my_api traefik/whoami

cat <<EOF > ~/web-lab/caddy-routes/Caddyfile
:80 {
    # Match /api and route to dummy backend
    handle_path /api/* {
        reverse_proxy host.docker.internal:8001
    }

    # Match everything else and serve files
    handle {
        root * /srv
        file_server
    }
}
EOF

docker run -d --name caddy_gateway -p 8089:80 \
  --add-host host.docker.internal:host-gateway \
  -v ~/web-lab/caddy-routes/Caddyfile:/etc/caddy/Caddyfile \
  -v ~/web-lab/caddy-routes:/srv caddy:alpine

```

* **Host Verification:** * Open `http://localhost:8089/` -> See "Frontend UI"
* Open `http://localhost:8089/api/` -> See the backend system data.



---

### Part 4: The Integration

#### Exercise 10: The Multi-Server Mesh (Docker Compose)

* **The Layman Problem:** In real-world enterprise environments, you don't use just one server type. You might use Nginx at the edge to block attacks, routing traffic to a legacy Apache billing app, and a modern Caddy websocket API.
* **Goal:** Deploy a unified architecture using Docker Compose.
* **Steps:**

```bash
mkdir -p ~/web-lab/mesh
cd ~/web-lab/mesh

# Create a legacy Apache app
mkdir apache-app
echo "<h1>Legacy Apache System</h1>" > apache-app/index.html

# Create the Nginx Edge Router
cat <<EOF > nginx.conf
events {}
http {
    server {
        listen 80;
        
        # Route to Apache
        location /legacy/ {
            proxy_pass http://apache-legacy/;
        }
        
        # Route to Caddy
        location /modern/ {
            proxy_pass http://caddy-modern/;
        }
    }
}
EOF

# Create the Compose stack
cat <<EOF > docker-compose.yml
version: '3.8'
services:
  edge-router:
    image: nginx:alpine
    ports:
      - "8090:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - apache-legacy
      - caddy-modern

  apache-legacy:
    image: httpd:alpine
    volumes:
      - ./apache-app:/usr/local/apache2/htdocs/

  caddy-modern:
    image: caddy:alpine
    command: caddy respond --listen :80 "Modern Caddy System Active"
EOF

# Deploy the mesh
docker compose up -d

```

* **Host Verification:** * Open `http://localhost:8090/legacy/` -> Routed through Nginx to Apache.
* Open `http://localhost:8090/modern/` -> Routed through Nginx to Caddy.