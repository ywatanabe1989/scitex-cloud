<!-- ---
!-- Timestamp: 2025-10-18 10:20:32
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/README.md
!-- --- -->

# SciTeX-Cloud

Django-based online platform for accelerating scientific workflows and manuscript preparation.

🌐 **Live Website**: https://scitex.ai

⚠️ **Development Status**: This project is under active development and in a conceptual phase. Some instructions may be outdated or incomplete. Please verify configurations and paths before deployment.

## Quick Start

```bash
# Clone and setup
git clone git@github.com/SciTeX-AI/scitex-cloud
cd scite-cloud
date && sudo apt-get install -y python3-dev build-essential

# Setup virtual environment
python3 -m venv .env
source .env/bin/activate

# Install dependencies
pip install -r docs/requirements/development.txt

# Initialize Django
python manage.py migrate
python manage.py collectstatic --noinput

# Run development server
./scripts/start_dev.sh

# Run tests
./tests/run_tests.sh --debug
```

## Project Structure

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `apps/` | Django applications | cloud_app, search_app, viz_app |
| `config/` | Django settings | settings/, nginx_confs/, uwsgi.ini |
| `static/` | Frontend assets | CSS, JavaScript, images |
| `templates/` | Base HTML templates | base.html, partials/ |
| `tests/` | Test suite | run_tests.sh, test_*.py |
| `scripts/` | Deployment scripts | start_dev.sh, start_prod.sh |
| `docs/` | Documentation | HOW_TO_SETUP.md, components.md |


## Applications

| App | Purpose | Key Features |
|-----|---------|--------------|
| `cloud_app` | Main platform | Landing, authentication, core UI |
| `search_app` | Search functionality | Document indexing, query processing |
| `viz_app` | Data visualization | Charts, plots, interactive displays |
| `engine_app` | Processing engine | Computational workflows |
| `doc_app` | Document management | File handling, version control |
| `code_app` | Code tools | Syntax highlighting, execution |

## Installation

### Development Setup
```bash
# Quick development setup
./scripts/start_dev.sh

# Manual setup - see HOW_TO_SETUP.md for details
python3 -m venv .env
source .env/bin/activate
pip install -r docs/requirements/development.txt
python manage.py migrate
python manage.py runserver
```

### Production Deployment
See [HOW_TO_SETUP.md](./docs/HOW_TO_SETUP.md) for comprehensive production setup including:
- Ubuntu server configuration with nginx and uWSGI
- SSL/HTTPS setup with Let's Encrypt
- Database configuration and optimization
- Security hardening and monitoring

## Development Workflow

### Testing
```bash
# Run all tests
./tests/run_tests.sh

# Run with debugging
./tests/run_tests.sh --debug

# Django-specific tests
python manage.py test

# Check code quality
python manage.py check
```

## Configuration

| Environment | Settings File | Purpose |
|-------------|---------------|---------|
| Development | `config/settings/development.py` | Debug enabled, SQLite |
| Production | `config/settings/production.py` | Security hardened, PostgreSQL |
| Base | `config/settings/base.py` | Common settings |

### Environment Variables
```bash
# Required for production
export SCITEX_DJANGO_SECRET_KEY="your-secret-key"
export DEBUG=False
export ALLOWED_HOSTS="your-domain.com"
export DATABASE_URL="postgres://..."
```

## API Endpoints

Base URL: `https://scitex.ai/api/`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health/` | GET | System health check |
| `/auth/` | POST | User authentication |
| `/search/` | GET/POST | Content search |
| `/documents/` | CRUD | Document management |

## Troubleshooting

### Common Issues
| Issue | Solution |
|-------|----------|
| Static files not loading | Run `python manage.py collectstatic` |
| Import errors | Activate virtual environment |
| Database errors | Run `python manage.py migrate` |
| Permission denied | Check file ownership and chmod +x scripts |

## License

MIT License - Anyone can edit, redistribute, and deploy this program under the terms of the MIT License.

## Contact
Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)

---
  sudo cp /home/ywatanabe/proj/SciTeX-Cloud/config/nginx_confs/scitex-https-fixed.conf /etc/nginx/sites-available/scitex-https.conf
  
  sudo nginx -t
  sudo systemctl reload nginx

<!-- EOF -->