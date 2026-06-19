### Docker Internals: 15 Core Exercises

#### Exercise 1: The Hello World Isolation

* **The Layman Problem:** You need to run a program to verify your system works, but you don't want that program leaving permanent junk files on your host computer.
* **Steps:** Pull and run the standard hello-world image. Notice how it executes its task and immediately exits, leaving your host system clean.

```bash
docker run hello-world

```

#### Exercise 2: Interactive Shell Inside a Container

* **The Layman Problem:** You need to explore the inside of a container as if it were a separate physical computer to see what folders and files actually exist inside the isolation boundary.
* **Steps:** Run an Alpine Linux container in interactive mode (`-it`) and execute a shell (`sh`). Run `ls` to view the filesystem, then type `exit` to return to your host.

```bash
docker run -it alpine sh
# Once inside:
ls -la
exit

```

#### Exercise 3: Inspecting Container Metadata

* **The Layman Problem:** You need to find hidden technical details about a running environment, like its internal IP address or exactly what folders are mounted, without actually logging into it.
* **Steps:** Start a detached container, grab its ID, and use the inspect command to output its complete JSON configuration.

```bash
docker run -d --name meta_test alpine sleep 1000
docker inspect meta_test
docker rm -f meta_test

```

#### Exercise 4: The Process Tree Reality

* **The Layman Problem:** You need to prove that containers are not heavy, isolated virtual machines, but actually just regular, restricted processes running directly on your host computer's processor.
* **Steps:** Run a container that sleeps. Then, on your host machine, use the standard Linux process command to find that exact sleep process running natively.

```bash
docker run -d --name process_test alpine sleep 7777
# Run this on your host to see the process:
ps aux | grep "sleep 7777"
docker rm -f process_test

```

#### Exercise 5: Exposing Ports to the Host

* **The Layman Problem:** A web server running inside a container is trapped behind the isolation wall. You need to open a specific door to let outside web browser traffic reach the application.
* **Steps:** Run an Nginx container and map your host's port 8080 to the container's internal port 80.

```bash
docker run -d --name web_server -p 8080:80 nginx:alpine
# Test it using curl or your browser at http://localhost:8080
curl http://localhost:8080
docker rm -f web_server

```

#### Exercise 6: Bind Mounts for Live File Sharing

* **The Layman Problem:** When you edit code on your computer, you don't want to completely rebuild the container every single time just to see the changes. You need the container to see your live files.
* **Steps:** Create a temporary folder on your host. Run an Alpine container and use `-v` to map that host folder to a folder inside the container.

```bash
mkdir ~/docker_bind_test
docker run -it -v ~/docker_bind_test:/mnt/test alpine sh
# Inside the container, create a file:
echo "Hello from inside" > /mnt/test/file.txt
exit
# Back on your host, read the file:
cat ~/docker_bind_test/file.txt

```

#### Exercise 7: Docker Volumes for Persistent Storage

* **The Layman Problem:** When a container is deleted, all the data inside it is destroyed forever. Databases need a safe, permanent vault to store files independent of the container's lifecycle.
* **Steps:** Create a Docker-managed volume, mount it to a container, write data to it, destroy the container, and mount the same volume to a *new* container to prove the data survived.

```bash
docker volume create my_database_data
docker run -it -v my_database_data:/data alpine sh -c "echo 'Permanent Data' > /data/save.txt"
# The container exits and is gone. Now spin up a new one:
docker run -it --rm -v my_database_data:/data alpine cat /data/save.txt

```

#### Exercise 8: CPU Throttling (cgroups)

* **The Layman Problem:** A buggy script might accidentally use 100% of the processor, freezing your entire computer. You need to strictly limit how much CPU power the container is allowed to draw.
* **Steps:** Run a container and restrict it to a maximum of 50% of a single CPU core using the `--cpus` flag.

```bash
docker run -it --rm --cpus="0.5" alpine sh -c "while true; do true; done"
# In a separate terminal on your host, run 'top' or 'htop' to verify it only uses 50% CPU.

```

#### Exercise 9: Memory Limits and Hard Stops

* **The Layman Problem:** You need to ensure an application cannot consume all your RAM and starve the rest of the system. If it tries, the system should forcefully kill it.
* **Steps:** Run a container with a strict memory limit of 64 Megabytes.

```bash
docker run -it --rm --memory="64m" alpine sh
# Inside the container, check available memory limits (if your host supports it):
cat /sys/fs/cgroup/memory/memory.limit_in_bytes
exit

```

#### Exercise 10: Writing a Reproducible Dockerfile

* **The Layman Problem:** You need a repeatable, text-based recipe to build your application's environment perfectly every time, rather than installing tools manually and forgetting the steps.
* **Steps:** Create a `Dockerfile`, define a base image, run an update command, and build your custom image.

```bash
cat <<EOF > Dockerfile
FROM alpine:latest
RUN apk add --no-cache curl
CMD ["curl", "--version"]
EOF
docker build -t my_curl_image .
docker run --rm my_curl_image

```

#### Exercise 11: Inspecting Image Layers

* **The Layman Problem:** Downloading an entire operating system every time you change one tiny line of code is too slow. You need to understand how Docker stacks files in layers so it only downloads what changed.
* **Steps:** Use the history command on the image you just built to see how each line in the Dockerfile created a distinct, cacheable layer.

```bash
docker history my_curl_image

```

#### Exercise 12: Creating an Isolated Bridge Network

* **The Layman Problem:** You want a specific web app and its database to talk securely to each other, without any other containers on the system being able to snoop on their network traffic.
* **Steps:** Create a custom bridge network and attach two containers to it.

```bash
docker network create secure_net
docker run -d --name secure_app1 --net secure_net alpine sleep 1000
docker run -d --name secure_app2 --net secure_net alpine sleep 1000

```

#### Exercise 13: Internal Container DNS Resolution

* **The Layman Problem:** Internal IP addresses change dynamically when containers restart. Programs need to reliably find each other using simple, permanent names instead of numbers.
* **Steps:** Using the two containers from Exercise 12, execute a ping command from one container to the other using solely the container's name.

```bash
docker exec -it secure_app1 ping -c 3 secure_app2
docker rm -f secure_app1 secure_app2

```

#### Exercise 14: Tailing Container Logs

* **The Layman Problem:** A background process crashed, and you need to see its error messages and print statements without having to log into the system or find a log file.
* **Steps:** Run a container that echoes text in a loop. Use the `docker logs` command to read its historical and live output.

```bash
docker run -d --name log_test alpine sh -c "while true; do echo 'Processing...'; sleep 2; done"
# View history:
docker logs log_test
# Tail live logs:
docker logs -f log_test
# (Ctrl+C to stop tailing)
docker rm -f log_test

```

#### Exercise 15: Pruning the Environment

* **The Layman Problem:** Over time, stopped containers, unused networks, and dangling image layers fill up your hard drive, causing hidden "out of space" errors.
* **Steps:** Run the system-wide prune command to permanently delete everything that is not actively running or attached to a running container.

```bash
docker system prune -a --volumes

```