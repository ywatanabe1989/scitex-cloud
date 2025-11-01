# Docker Deployment

Docker-based deployment for SciTeX Cloud.

## Structure

```
deployment/docker/
├── common/          # Shared resources
│   ├── lib/        # Source libraries (.src)
│   ├── monitoring/ # Health check scripts
│   ├── scripts/    # Utility scripts
│   ├── nginx/      # Nginx configs
│   └── docs/       # Documentation
│
├── docker_dev/     # Development
├── docker_prod/    # Production
└── docker_nas/     # NAS/Home server
```

## Quick Start

```bash
# From project root
make start                    # Dev (default)
make ENV=prod start           # Production
make ENV=nas start            # NAS
```

## Documentation

- `common/docs/DOCKERFILE_OPTIMIZATION.md` - Build optimization
- `common/docs/SCITEX_PACKAGE_INSTALLATION.md` - Package strategy
- `common/docs/SETUP_VERIFICATION.md` - Verification guide
- `docker_dev/README.md` - Development setup
- `docker_prod/README.md` - Production setup
- `docker_nas/README.md` - NAS setup

## See Also

- Root: `make help`
- Manual deployment: `deployment/manual/`
- Environment templates: `deployment/envs/`
