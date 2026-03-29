# PotionLab Docker Compose Stack - Operations Runbook

This runbook covers deployment, verification, testing, and teardown procedures for the PotionLab Docker Compose stack.

## Overview

The stack consists of three services:
- **api**: PotionLab FastAPI application (port 8000)
- **db**: PostgreSQL 16 database with persistent storage
- **redis**: Redis 7 cache

## Prerequisites

- Docker Engine 24.0+ with Compose v2
- Minimum 2GB available RAM
- Ports 8000, 5432, and 6379 available

## Environment Setup

1. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Set PostgreSQL password** (edit `.env`):
   ```bash
   POSTGRES_PASSWORD=your_secure_password_here
   ```

   > **Security Note**: Never commit `.env` to version control. Only `.env.example` should be tracked.

## Launch Procedures

### 1. Start the Full Stack

```bash
docker compose up --build -d
```

**What this does**:
- Builds the API Docker image with multi-stage uv build
- Pulls PostgreSQL 16 Alpine and Redis 7 Alpine images
- Creates named volume `postgres_data` for database persistence
- Starts all services with health checks enabled
- Runs in detached mode (`-d`)

**Expected output**:
```
[+] Building 45.2s (14/14) FINISHED
[+] Running 4/4
 ✔ Network lecture-notes_default        Created
 ✔ Container lecture-notes-db-1         Started (healthy)
 ✔ Container lecture-notes-redis-1      Started (healthy)
 ✔ Container lecture-notes-api-1        Started
```

### 2. Monitor Service Health

Wait for all services to reach `healthy` status:

```bash
docker compose ps
```

**Expected output**:
```
NAME                    STATUS              PORTS
lecture-notes-api-1     Up (healthy)        0.0.0.0:8000->8000/tcp
lecture-notes-db-1      Up (healthy)        5432/tcp
lecture-notes-redis-1   Up (healthy)        6379/tcp
```

**Troubleshooting**: If services show `starting` after 30s, check logs:
```bash
docker compose logs api
docker compose logs db
docker compose logs redis
```

## Verification Procedures

### 1. API Health Check

```bash
curl -s http://localhost:8000/health | jq
```

**Expected response**:
```json
{
  "status": "ok"
}
```

**Troubleshooting**:
- `Connection refused`: API hasn't started yet, wait 10s and retry
- `502 Bad Gateway`: Check `docker compose logs api` for startup errors

### 2. Redis Connectivity

```bash
docker compose exec redis redis-cli ping
```

**Expected output**:
```
PONG
```

### 3. PostgreSQL Connectivity

```bash
docker compose exec db psql -U postgres -d potionlab -c '\dt'
```

**Expected output**: List of database tables (potionlab schema)

### 4. API Database Connection

Verify the API is using PostgreSQL (not SQLite):

```bash
docker compose logs api | grep -i "database"
```

**Look for**: Connection logs mentioning `postgresql://` (not `sqlite://`)

## Testing Procedures

### 1. Run API Test Suite

Execute the full pytest suite inside the container:

```bash
docker compose exec api pytest -q
```

**Expected output**:
```
59 passed in 2.45s
```

### 2. Create Test Data

Seed the database with sample cocktails:

```bash
docker compose exec api python scripts/seed.py
```

### 3. Verify API Endpoints

Test cocktail listing:

```bash
curl -s http://localhost:8000/api/v1/cocktails/ | jq '. | length'
```

**Expected output**: Number of seeded cocktails (e.g., `22`)

## Maintenance Procedures

### View Logs

**All services**:
```bash
docker compose logs -f
```

**Specific service**:
```bash
docker compose logs -f api
docker compose logs -f db
docker compose logs -f redis
```

### Restart Services

**All services**:
```bash
docker compose restart
```

**Specific service**:
```bash
docker compose restart api
```

### Rebuild After Code Changes

```bash
docker compose up --build -d
```

## Teardown Procedures

### 1. Stop Services (Preserve Data)

```bash
docker compose down
```

**What this does**:
- Stops all containers
- Removes containers and networks
- **Preserves** the `postgres_data` volume (database persists)

### 2. Full Teardown (Delete All Data)

```bash
docker compose down -v
```

**What this does**:
- Stops all containers
- Removes containers and networks
- **Deletes** the `postgres_data` volume (**permanent data loss**)

> **Warning**: Use `-v` flag only when you want to completely reset the database.

### 3. Remove Dangling Images

After multiple rebuilds, clean up unused images:

```bash
docker image prune -f
```

## Troubleshooting Guide

### API Won't Start

**Symptoms**: `docker compose ps` shows API as `restarting` or `unhealthy`

**Diagnosis**:
```bash
docker compose logs api --tail=50
```

**Common causes**:
- Missing environment variables: Check `POTION_DATABASE_URL` in compose.yaml
- Database not ready: Ensure `db` service is `healthy` before API starts
- Port conflict: Check if port 8000 is already in use (`lsof -i :8000`)

### Database Connection Errors

**Symptoms**: API logs show `connection refused` or `could not connect to server`

**Diagnosis**:
```bash
docker compose exec db pg_isready -U postgres
```

**Common causes**:
- PostgreSQL still initializing: Wait 10s after `docker compose up`
- Wrong credentials: Verify `POSTGRES_PASSWORD` matches in `.env` and compose.yaml
- Network issue: Check `docker network ls` and ensure services are on same network

### Redis Connection Errors

**Symptoms**: API logs show Redis connection warnings

**Diagnosis**:
```bash
docker compose exec redis redis-cli ping
```

**Common causes**:
- Redis not started: Check `docker compose ps` for Redis health status
- Wrong URL format: Verify `POTION_REDIS_URL=redis://redis:6379` (no password for dev)

### Data Persistence Issues

**Symptoms**: Database data disappears after `docker compose down`

**Diagnosis**:
```bash
docker volume ls | grep postgres_data
```

**Solution**: Never use `docker compose down -v` unless you want to delete data permanently. Use `docker compose down` to preserve volumes.

## Production Considerations

This stack is designed for **development and testing**. For production deployments:

1. **Security**:
   - Use Docker secrets instead of `.env` files
   - Enable PostgreSQL SSL/TLS connections
   - Configure Redis authentication (`requirepass`)
   - Run containers as non-root users

2. **Scalability**:
   - Use external managed PostgreSQL (e.g., AWS RDS, Cloud SQL)
   - Use external managed Redis (e.g., ElastiCache, Cloud Memorystore)
   - Deploy API with replicas behind a load balancer

3. **Monitoring**:
   - Add Prometheus metrics exporters
   - Configure container log aggregation (e.g., Loki, CloudWatch)
   - Set up alerting for service health checks

4. **Backups**:
   - Schedule PostgreSQL backups with `pg_dump`
   - Store backups in object storage (S3, GCS)
   - Test restore procedures regularly

## Quick Reference

| Task | Command |
|------|---------|
| Start stack | `docker compose up --build -d` |
| Stop stack (keep data) | `docker compose down` |
| Stop stack (delete data) | `docker compose down -v` |
| View all logs | `docker compose logs -f` |
| Check service health | `docker compose ps` |
| API health check | `curl http://localhost:8000/health` |
| Redis ping | `docker compose exec redis redis-cli ping` |
| Run tests | `docker compose exec api pytest -q` |
| Seed database | `docker compose exec api python scripts/seed.py` |
| PostgreSQL shell | `docker compose exec db psql -U postgres -d potionlab` |
| Restart API | `docker compose restart api` |

## Support

For issues or questions about the PotionLab stack:
1. Check logs: `docker compose logs <service-name>`
2. Review this runbook's troubleshooting section
3. Consult project documentation: `README.md`
