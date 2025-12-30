# ETL Data Pipeline

![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/mrpbennett/etl-pipeline?style=for-the-badge)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)

![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/mrpbennett/etl-pipeline/sourcery-pr.yml?style=for-the-badge&label=sourcery)
![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/mrpbennett/etl-pipeline/python-package.yml?style=for-the-badge&label=build)

![FastAPI](https://img.shields.io/badge/fastapi-009688.svg?&style=for-the-badge&logo=fastapi&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-150458.svg?&style=for-the-badge&logo=pandas&logoColor=white)
![Redis](https://img.shields.io/badge/redis-DC382D.svg?&style=for-the-badge&logo=redis&logoColor=white)
![Postgres](https://img.shields.io/badge/postgresql-4169E1.svg?&style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-2496ED.svg?&style=for-the-badge&logo=docker&logoColor=white) ![React](https://img.shields.io/badge/react-35495e.svg?&style=for-the-badge&logo=react&logoColor=61DAFB)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-gray.svg?&style=for-the-badge&logo=tailwindcss&logoColor=06B6D4)

## Objective

Create a data pipeline that ingests user data via an API, processes and stores it, and then retrieves it in a serialized format.

### Components

1. **Data Source**: Random API for fake user data
2. **Python & Pandas**: For programming and data manipulation.
3. **Redis**: Caching recent data for quick access.
4. **Postgres**: Long-term data storage.
5. **FastAPI** For an API endpoint for data retrieval
6. **Docker**: Containerization of the entire pipeline.

### Steps

![assets/flow.png](https://github.com/mrpbennett/etl-pipeline/blob/v2/assets/flowv2.png?raw=true)

1. **Data Ingestion**:
   - Python script to fetch data random user data from an API.
   - Validate the data before processing.
   - Pandas for data cleaning and transformation.
2. **Caching Layer**:
   - Redis setup for caching recent User data and set a TTL.
   - Python logic for data retrieval from Redis and Postgres.
3. **Data Storage**:
   - Design and implement a Postgres database schema for the user data.
   - Make sure PII is hashed before putting into storage
   - Store processed data into Postgres.
4. **Data Retrieval**:
   - API endpoint (e.g., using FastAPI) for data retrieval.
5. **Dockerization**:
   - Dockerfile for the Python application.
   - Docker Compose for orchestrating Redis and Postgres services.
6. **Testing and Deployment**:
   - Unit tests for pipeline components.

### Learning Outcomes

- Data pipeline architecture.
- Skills in Python, Pandas, Redis, Postgres, FastAPI and Docker.

### Further Enhancements

- ~~Front-end dashboard for data display.~~
- Advanced data processing features.

## How to test the project

Clone the repo

```bash
git clone https://github.com/mrpbennett/etl-pipeline.git
```

`cd` into the cloned repo and run `docker compose up`

```bash
docker compose up
```

Then head over to the URL to access the front end to see where the data is stored

```text
http://120.0.0.1:5173
```

## Operating a Living System (Linux Operations Guide)

Since this project is now running on your Ubuntu VM, here is how you can monitor and manage it like a real production system.

### 1. Basic Status Checks
- **Check running containers**: `docker compose ps` (Shows what's up and what ports are used).
- **View live logs**: `docker compose logs -f` (Follow logs in real-time).
- **Check specific service logs**: `docker compose logs -f pipeline` (Focus on the ETL process).

### 2. Managing the System
- **Stop everything**: `docker compose stop`
- **Start everything**: `docker compose start`
- **Restart after changes**: `docker compose up -d` (Docker is smart; it only restarts what changed).
- **Auto-restart on Reboot**: The `restart: unless-stopped` policy in `docker-compose.yml` ensures that if your VM restarts, Docker will automatically start your containers back up.

### 3. Linux & System Learning Exercises
Here are some "tasks" you can do to practice Linux skills using this project:

- **Resource Monitoring**: Run `htop` (you might need to install it: `sudo apt install htop`). Find the Python and Postgres processes and see how much CPU/RAM they use.
- **Disk Usage**: Use `df -h` to see your VM's disk space. Use `du -sh ~/system_practice` to see how big the project folder is.
- **Log Grepping**: Find errors in your logs without scrolling: `docker compose logs | grep ERROR`.
- **Database Exploration**: Exec into the database to run queries manually:
  `docker exec -it system_practice-postgres-1 psql -U postgres -d prac_db`
- **Networking**: Use `netstat -tuln` or `ss -tuln` to see all ports currently listening on your Ubuntu VM. You should see `5173` and `5433` there.

---
## ⭐ Stargazers

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=mrpbennett/etl-pipeline&type=Date)](https://star-history.com/#mrpbennett/etl-pipeline&Date)

</div>
