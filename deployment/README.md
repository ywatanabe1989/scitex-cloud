# SciTeX Cloud - Deployment

Deployment configurations for SciTeX Cloud.

## Structure

```
deployment/
├── docker/          # Docker-based deployments
│   ├── common/     # Shared resources
│   ├── docker_dev/ # Development
│   ├── docker_prod/# Production
│   └── docker_nas/ # NAS/Home server
│
├── manual/         # Manual system deployments
│   ├── nginx/      # Nginx setup
│   ├── postgres/   # PostgreSQL setup
│   ├── uwsgi/      # uWSGI setup
│   ├── gitea/      # Gitea setup
│   └── systemd/    # Systemd services
│
└── envs/           # Environment variable templates
    ├── dev.example
    ├── prod.example
    └── nas.example
```

## Quick Start

### Docker (Recommended)

```bash
# From project root
make start                    # Dev
make ENV=prod start           # Production
make ENV=nas start            # NAS

# See docker/README.md for details
```

### Manual Deployment

```bash
# See manual/nginx/README.md
# See manual/postgres/README.md
# See manual/uwsgi/README.md
```

## Environment Variables

Place `.env` files in `/SECRET/`:
- `SECRET/.env.dev`
- `SECRET/.env.prod`
- `SECRET/.env.nas`

Templates: `envs/*.example`

## Documentation

- `docker/README.md` - Docker deployments
- `docker/common/docs/` - Technical documentation
- `manual/*/README.md` - Manual setup guides

## See Also

- Root Makefile - `make help`
- Docker deployment - `deployment/docker/README.md`
