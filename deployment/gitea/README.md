# Gitea Deployment for SciTeX Cloud

This directory contains all Gitea-related deployment files, scripts, and documentation.

## 📁 Directory Structure

```
deployment/gitea/
├── README.md                         # This file - start here
├── GITEA_QUICKSTART.md              # Setup guide for first-time users
├── IMPLEMENTATION_COMPLETE.md        # ✅ What's been implemented
├── INTEGRATION_PROGRESS.md          # Detailed progress tracking
├── get-api-token.md                 # How to get API token
├── docker-compose.gitea-dev.yml     # Docker Compose configuration
├── start-dev.sh                     # 🚀 Start Gitea (executable)
└── stop-dev.sh                      # 🛑 Stop Gitea (executable)
```

## 🚀 Quick Start

### 1. Start Gitea
```bash
./deployment/gitea/start-dev.sh
# Opens on http://localhost:3000
```

### 2. Access Gitea
- **Web UI:** http://localhost:3000
- **SSH:** localhost:2222
- **User:** scitex
- **API:** http://localhost:3000/api/v1

### 3. Stop Gitea
```bash
./deployment/gitea/stop-dev.sh
```

## 📚 Documentation Guide

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **README.md** | Overview and quick reference | Start here |
| **GITEA_QUICKSTART.md** | First-time setup instructions | Setting up Gitea |
| **get-api-token.md** | Get API token for Django | After Gitea setup |
| **IMPLEMENTATION_COMPLETE.md** | What's implemented and working | Understanding features |
| **INTEGRATION_PROGRESS.md** | Technical implementation details | Development reference |

## ✅ Current Status

**Gitea Integration:** ✅ Complete and working!

- ✅ Gitea running locally
- ✅ Django API client implemented
- ✅ Project model updated
- ✅ Web UI integration complete
- ✅ GitHub import supported
- ✅ Local file workflows working

See `IMPLEMENTATION_COMPLETE.md` for full details.

## 🔧 Development Commands

```bash
# Container management
docker ps | grep gitea                 # Check if running
docker logs scitex-gitea-dev          # View logs
docker stop scitex-gitea-dev          # Stop container
docker start scitex-gitea-dev         # Start container

# API testing
source deployment/dotenvs/dotenv.dev
curl -H "Authorization: token $SCITEX_CLOUD_GITEA_TOKEN" \
  http://localhost:3000/api/v1/user/repos
```

## 📖 Related Documentation

- **Production deployment:** `TODOS/GIT_HOSTING.md`
- **Architecture:** `docs/INSTITUTIONAL_DEPLOYMENT_ARCHITECTURE.md`
- **Integration roadmap:** `docs/GITEA_INTEGRATION_ROADMAP.md`
- **Local file support:** `docs/NATIVE_LOCAL_FILE_SUPPORT.md`

## 🎯 Next Steps

1. **Test via Web UI:** Start Django server and create a project
2. **Import from GitHub:** Try importing your own repository
3. **Production planning:** When ready, see `TODOS/GIT_HOSTING.md`

---

**Everything is organized and ready to use!** 🎉
