# SciTeX Cloud - Docker Quick Start

All Docker configuration is in `containers/docker/` directory.

## First Time Setup

```bash
# 1. Stop old server (if running)
./server -s  # or: pkill -f uwsgi

# 2. Go to docker directory
cd containers/docker

# 3. Create environment file
cp .env.example .env

# 4. Edit .env (optional for development)
nano .env

# 5. Start everything
docker-compose up -d

# 6. Run migrations
docker-compose exec web python manage.py migrate

# 7. Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# 8. Create admin user
docker-compose exec web python manage.py createsuperuser

# 9. Access at http://localhost:8000
```

## Or Use Makefile (from project root)

```bash
# One command setup
make setup

# View logs
make logs

# Create superuser
make createsuperuser
```

## Daily Usage

```bash
# Start
make up

# Stop
make down

# View logs
make logs

# Django shell
make shell

# Run tests
make test
```

## Directory Structure

```
scitex-cloud/
├── containers/docker/          # All Docker files here
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── .env (your config)
│   ├── .env.example
│   ├── nginx/
│   └── scripts/
├── Makefile                    # Convenience commands
├── apps/                       # Your Django apps
├── config/                     # Django settings
└── ...
```

## Benefits Over Old System

✅ No more uwsgi configuration
✅ No more permission issues
✅ No more systemd services
✅ No more chmod/chown headaches
✅ Works the same everywhere
✅ Easy to scale

## Troubleshooting

### Port 8000 already in use
```bash
sudo lsof -i :8000
kill -9 <PID>
```

### Start fresh
```bash
make clean
make setup
```

### View all logs
```bash
cd containers/docker
docker-compose logs -f
```

## See More

- Detailed docs: `containers/docker/README.md`
- Production setup: `containers/docker/docker-compose.prod.yml`
