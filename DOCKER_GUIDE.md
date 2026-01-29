# Docker Guide for Beginners

This guide explains what Docker is, how the Dockerfile works, and how to use it to run this application.

---

## What is Docker?

Docker is a tool that packages your application and all its dependencies into a **container**. Think of a container like a lightweight, portable box that contains everything your app needs to run:

- The operating system (Linux)
- Python and its version
- All the libraries your code uses
- Your application code

**Why use Docker?**
- **Consistency**: The app runs the same way on your laptop, your colleague's laptop, and in the cloud
- **No "it works on my machine" problems**: Everyone uses the exact same environment
- **Easy deployment**: Upload the container to any cloud provider and it just works

---

## What is a Dockerfile?

A **Dockerfile** is a text file with instructions that tell Docker how to build your container. It's like a recipe that Docker follows step-by-step.

---

## Our Dockerfile Explained Line-by-Line

Here's the complete Dockerfile with detailed explanations:

```dockerfile
FROM python:3.13-slim
```

### Line 1: `FROM python:3.13-slim`

**What it does**: This is the starting point (base image) for our container.

- `python:3.13` means we want Python version 3.13 pre-installed
- `-slim` means we want a smaller version that only includes essential components (saves disk space and download time)

Think of it like choosing a pre-configured computer template that already has Python installed.

---

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
```

### Lines 2-4: `ENV` (Environment Variables)

**What it does**: Sets environment variables that configure how Python and the app behave.

| Variable | Value | Purpose |
|----------|-------|---------|
| `PYTHONDONTWRITEBYTECODE` | `1` | Prevents Python from creating `.pyc` files (compiled bytecode). Keeps the container clean. |
| `PYTHONUNBUFFERED` | `1` | Makes Python output appear immediately in logs instead of being buffered. Helps with debugging. |
| `PORT` | `8080` | The port number where the web app will listen. Google Cloud Run expects port 8080. |

---

```dockerfile
WORKDIR /app
```

### Line 5: `WORKDIR /app`

**What it does**: Creates a folder called `/app` inside the container and makes it the "current directory" for all following commands.

It's like running `mkdir /app && cd /app` on a regular computer.

---

```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
```

### Line 6: `COPY --from=...` (Multi-stage copy)

**What it does**: Copies the `uv` package installer from another Docker image into our container.

- `ghcr.io/astral-sh/uv:latest` is the official uv Docker image
- `/uv` and `/uvx` are the executable files we're copying
- `/bin/` is where we put them so they can be run from anywhere

**What is uv?**
`uv` is a modern Python package installer that's 10-100x faster than the traditional `pip`. It's written in Rust and significantly speeds up the container build process.

---

```dockerfile
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*
```

### Lines 7-11: `RUN apt-get...` (Install System Dependencies)

**What it does**: Installs system-level software needed to compile some Python packages.

| Package | Purpose |
|---------|---------|
| `gcc` | C compiler - needed to compile Python packages with C extensions |
| `libxml2-dev` | XML parsing library - required by `lxml` package |
| `libxslt-dev` | XSLT transformation library - also required by `lxml` |

**Breaking down the command**:
- `apt-get update` - Refreshes the list of available packages
- `apt-get install -y` - Installs packages (`-y` means "yes to all prompts")
- `&&` - Run the next command only if the previous one succeeds
- `\` - Continues the command on the next line (for readability)
- `rm -rf /var/lib/apt/lists/*` - Deletes cached package lists to reduce container size

---

```dockerfile
COPY requirements.txt .
```

### Line 12: `COPY requirements.txt .`

**What it does**: Copies the `requirements.txt` file from your computer into the container.

- First argument: source file on your computer
- Second argument: destination in the container (`.` means current directory, which is `/app`)

**Why copy this first?**
Docker caches each step. If `requirements.txt` hasn't changed, Docker will reuse the cached installed packages instead of reinstalling them. This makes rebuilds much faster.

---

```dockerfile
RUN uv pip install --system --no-cache -r requirements.txt
```

### Line 13: `RUN uv pip install...`

**What it does**: Installs all Python packages listed in `requirements.txt`.

| Flag | Purpose |
|------|---------|
| `--system` | Install packages into the system Python (not a virtual environment) |
| `--no-cache` | Don't cache downloaded packages (keeps container smaller) |
| `-r requirements.txt` | Read package names from this file |

This installs: `flask`, `requests`, `beautifulsoup4`, `pandas`, `lxml`, and `gunicorn`.

---

```dockerfile
COPY app.py .
COPY scrape.py .
```

### Lines 14-15: `COPY` (Application Code)

**What it does**: Copies your Python application files into the container.

- `app.py` - The Flask web application
- `scrape.py` - The web scraping logic

**Why copy code last?**
Code changes more frequently than dependencies. By copying code last, Docker can reuse the cached layers for Python installation when only code changes.

---

```dockerfile
EXPOSE 8080
```

### Line 16: `EXPOSE 8080`

**What it does**: Documents that the container listens on port 8080.

This is informational metadata - it doesn't actually open the port. The port is opened when you run the container with `-p 8080:8080`.

---

```dockerfile
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
```

### Line 17: `CMD` (Startup Command)

**What it does**: Specifies the command that runs when the container starts.

**Breaking it down**:

| Part | Meaning |
|------|---------|
| `exec` | Replaces the shell process with gunicorn (better for signal handling) |
| `gunicorn` | Production-grade Python web server |
| `--bind :$PORT` | Listen on the port specified by the PORT environment variable (8080) |
| `--workers 1` | Use 1 worker process (Cloud Run manages scaling externally) |
| `--threads 8` | Each worker handles 8 concurrent requests using threads |
| `--timeout 0` | No timeout (Cloud Run manages timeouts externally) |
| `app:app` | Run the `app` object from the `app.py` file |

---

## How to Use Docker

### Prerequisites

1. **Install Docker Desktop**:
   - Windows/Mac: Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   - Linux: Follow instructions at [docs.docker.com/engine/install](https://docs.docker.com/engine/install)

2. **Verify installation**:
   ```bash
   docker --version
   ```

### Building the Container

Open a terminal in the project folder and run:

```bash
docker build -t webscraper-olj .
```

**Explanation**:
- `docker build` - Command to build a container image
- `-t webscraper-olj` - Name (tag) for the image
- `.` - Use the Dockerfile in the current directory

**What happens**:
1. Docker reads the Dockerfile
2. Executes each instruction in order
3. Creates a container image you can run

First build takes a few minutes (downloading base image, installing packages). Subsequent builds are faster due to caching.

### Running the Container

```bash
docker run -p 8080:8080 webscraper-olj
```

**Explanation**:
- `docker run` - Start a container from an image
- `-p 8080:8080` - Map port 8080 on your computer to port 8080 in the container
- `webscraper-olj` - Name of the image to run

**Access the app**: Open your browser to `http://localhost:8080`

### Stopping the Container

Press `Ctrl+C` in the terminal, or run:

```bash
docker ps          # List running containers
docker stop <ID>   # Stop by container ID
```

### Useful Docker Commands

| Command | Purpose |
|---------|---------|
| `docker images` | List all images on your computer |
| `docker ps` | List running containers |
| `docker ps -a` | List all containers (including stopped) |
| `docker logs <ID>` | View container output/logs |
| `docker rm <ID>` | Delete a stopped container |
| `docker rmi <name>` | Delete an image |

---

## Deploying to Google Cloud Run

Once your container works locally, deploy it to the cloud:

```bash
# 1. Build and upload to Google Cloud
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/webscraper-olj

# 2. Deploy to Cloud Run
gcloud run deploy webscraper-olj \
  --image gcr.io/YOUR_PROJECT_ID/webscraper-olj \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated
```

Cloud Run will give you a URL like `https://webscraper-olj-abc123-as.a.run.app` where your app is live.

---

## Troubleshooting

### "Cannot connect to Docker daemon"
- Make sure Docker Desktop is running

### Build fails at `apt-get install`
- Check your internet connection
- Try running `docker build --no-cache -t webscraper-olj .`

### Container starts but app doesn't respond
- Check logs: `docker logs <container_id>`
- Verify port mapping is correct (`-p 8080:8080`)

### "Package not found" errors
- Ensure `requirements.txt` exists and is correct
- Check that all package names are spelled correctly

---

## Summary

| Concept | Description |
|---------|-------------|
| **Docker** | Tool to package apps in portable containers |
| **Dockerfile** | Recipe/instructions to build a container |
| **Image** | The built container template (like a snapshot) |
| **Container** | A running instance of an image |
| **Base Image** | Starting point (`python:3.13-slim`) |
| **Layer** | Each Dockerfile instruction creates a cached layer |

The key benefit: Once containerized, your app runs identically everywhere - your laptop, a colleague's machine, or Google Cloud Run.
