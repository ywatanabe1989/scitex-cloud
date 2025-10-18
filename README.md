# SciTeX Cloud

**Open-source scientific research platform for researchers and academics**

🌐 **Live Website**: https://scitex.ai
📚 **Documentation**: [./docs/](./docs/)
🔧 **Version**: 0.1.0-alpha

---

## ⚠️ Development Status

This project is under active development. Not all functionalities are implemented. Any data may be lost until stable version is released. **Modules may work locally better.**

---

## Overview

SciTeX Cloud is a Django-based web platform that provides an integrated ecosystem for scientific research, from literature discovery to manuscript publication.

### Core Modules

- **Scholar** - Literature discovery and analysis
- **Writer** - AI-enhanced scientific writing
- **Code** - Data analysis and computing
- **Viz** - Publication-quality graphics

### Deployment Options

- **SciTeX Cloud** - Web interface at scitex.ai (this repository)
- **SciTeX Local** - Full control, no internet required

---

## Quick Start

### Development Setup

```bash
# Clone repository
git clone git@github.com:ywatanabe1989/scitex-cloud.git
cd scitex-cloud

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp deployment/dotenvs/dotenv.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Start development server
./server.sh
```

Access at: http://127.0.0.1:8000/

---

## Project Structure

```
scitex-cloud/
├── apps/                    # Django applications
│   ├── auth_app/           # Authentication & signup
│   ├── cloud_app/          # Landing page & main UI
│   ├── code_app/           # Code analysis module
│   ├── scholar_app/        # Literature discovery
│   ├── writer_app/         # Scientific writing
│   ├── viz_app/            # Data visualization
│   ├── profile_app/        # User profiles & settings
│   ├── project_app/        # Repository management
│   ├── social_app/         # Social features (follow, star, explore)
│   ├── dev_app/            # Design system & developer tools
│   └── gitea_app/          # Git hosting integration
│
├── config/                  # Django configuration
│   ├── settings/           # Settings files (dev, prod, shared)
│   └── urls.py             # Main URL routing
│
├── static/                  # Frontend assets
│   ├── css/                # Stylesheets
│   │   ├── common/         # Shared styles (colors, typography, settings-layout)
│   │   ├── components/     # Component styles (hero, buttons)
│   │   ├── pages/          # Page-specific styles
│   │   └── base/           # Base & overrides
│   ├── js/                 # JavaScript
│   └── images/             # Icons, logos
│
├── templates/               # Base templates
│   └── partials/           # Reusable components (header, footer)
│
├── deployment/              # Deployment configurations
│   ├── dotenvs/            # Environment variable templates
│   ├── gitea/              # Gitea integration setup
│   ├── nginx/              # Nginx configurations
│   ├── postgres/           # PostgreSQL setup
│   └── uwsgi/              # uWSGI configurations
│
├── scripts/                 # Utility scripts
│   ├── server/             # Server management
│   ├── deployment/         # Deployment helpers
│   ├── docs_building/      # Documentation generation
│   └── utils/              # Formatting & utilities
│
├── docs/                    # Documentation
│   └── archive/            # Historical documentation
│
├── data/                    # User data (gitignored)
│   ├── db/                 # Database files
│   ├── ssh_keys/           # SSH keys (sensitive)
│   └── users/              # User workspaces
│
└── tests/                   # Test suite

```

---

## Key Features

### User Profile System
- Public profile with bio, institution, and research interests
- Git hosting profiles (GitHub, GitLab, Bitbucket)
- Tabbed interface: Overview, Repositories, Projects, Stars
- Settings organized by sections (Personal, Access & Security)

### Profile Settings
- **Public Profile** - Bio, location, links, Git hosting profiles
- **Account** - Email change, password change, delete account
- **Appearance** - Theme preferences (dark mode default)
- **Git Integrations** - GitHub, GitLab, Bitbucket tokens (masked display)
- **SSH & GPG Keys** - Tabbed interface for key management
- **API Keys** - API token management

### Repository Management
- GitHub-style repository interface
- Import from GitHub/GitLab/Bitbucket
- Collaborator management (Read, Write, Admin roles)
- Visibility controls (Public/Private)
- GitHub-style deletion confirmation

### Design System
- Theme-responsive (light/dark modes)
- GitHub-inspired UI components
- Hero component with multiple gradient variants
- Consistent color palette across all pages
- Accessible at `/dev/design/`

---

## Environment Variables

Create a `.env` file or use `deployment/dotenvs/dotenv.{dev,prod}`:

```bash
# Django
SCITEX_DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True  # False in production

# Database
SCITEX_DB_ENGINE=sqlite3  # or postgresql
SCITEX_DB_NAME=scitex_cloud.db

# Git Integration (optional)
SCITEX_CLOUD_GITEA_URL=http://localhost:3000
SCITEX_CLOUD_GITEA_TOKEN=your-gitea-token

# Email (optional)
SCITEX_EMAIL_HOST=smtp.gmail.com
SCITEX_EMAIL_PORT=587
```

See `deployment/dotenvs/dotenv.example` for complete list.

---

## Development

### Running the Server

```bash
# Development server
./server.sh

# Or directly with Django
python manage.py runserver
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Static Files

```bash
# Collect static files for production
python manage.py collectstatic --noinput
```

---

## Deployment

See [deployment/README.md](./deployment/README.md) for detailed deployment instructions including:

- **Nginx** configuration
- **uWSGI** setup
- **PostgreSQL** database
- **Gitea** integration (optional)
- SSL/HTTPS setup

Quick production deployment:
```bash
# Set environment
export SCITEX_ENV=prod

# Run deployment scripts
./scripts/deployment/setup_postgres.sh
./scripts/deployment/configure_nginx_system.sh

# Start services
systemctl start scitex-cloud
systemctl start nginx
```

---

## Architecture

### Technology Stack
- **Backend**: Django 4.2+
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: HTML5, CSS3, JavaScript
- **Server**: Nginx + uWSGI (production)
- **Version Control**: Git + Gitea integration

### Design Philosophy
- **Project-centric**: All modules (Scholar, Code, Viz, Writer) are linked to projects
- **GitHub-inspired UI**: Familiar interface for developers and researchers
- **Theme-responsive**: Full light/dark mode support
- **Open source**: 100% MIT licensed

---

## Applications

| App | Path | Purpose |
|-----|------|---------|
| `auth_app` | `/auth/` | User authentication, signup, login |
| `cloud_app` | `/` | Landing page, about, donate |
| `profile_app` | `/profile/` | User profiles and settings |
| `project_app` | `/<username>/<repo>/` | Repository management |
| `social_app` | `/social/` | Explore, follow, star, notifications |
| `scholar_app` | `/scholar/` | Literature search and discovery |
| `writer_app` | `/writer/` | Manuscript writing interface |
| `code_app` | `/code/` | Code analysis and execution |
| `viz_app` | `/viz/` | Data visualization |
| `dev_app` | `/dev/` | Design system and developer tools |

---

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow Django best practices
- Use `apps/XXX_app/` format for applications
- Keep files organized (no files in project root)
- Use theme-responsive CSS variables

---

## Database Migrations

The project includes migrations for:
- User profiles with SSH keys and Git integrations
- Project/Repository models with Git metadata
- Social features (follows, stars, activities)

**Current migrations:**
- `profile_app`: 4 migrations (SSH keys, Git tokens, hosting profiles)
- `project_app`: 8 migrations (Git integration, hypotheses removal)

---

## Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
python manage.py runserver 8080
```

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
```

**Database errors:**
```bash
# Reset database (development only!)
rm data/db/sqlite/scitex_cloud.db
python manage.py migrate
```

**Permission errors:**
```bash
chmod +x scripts/server/start
chmod +x deployment/gitea/*.sh
```

---

## Security

- SSH keys stored in `data/ssh_keys/` (gitignored)
- User data in `data/users/` (gitignored)
- Tokens displayed as masked (first 4 + last 4 chars)
- Environment variables for secrets (never committed)
- GitHub push protection enabled

---

## License

MIT License - See [LICENSE](./LICENSE) for details.

**100% Open Source** - Anyone can edit, redistribute, and deploy this program.

---

## Contact & Community

- **GitHub**: https://github.com/SciTeX-AI
- **Author**: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)
- **Issues**: https://github.com/ywatanabe1989/scitex-cloud/issues

---

## Acknowledgments

Built by researchers, for researchers. Community-driven development.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- EOF -->
