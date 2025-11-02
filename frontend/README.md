# Frontend Tooling

All JavaScript/TypeScript build tooling and dependencies for SciTeX Cloud.

## Structure

```
frontend/
├── package.json           - NPM dependencies and scripts
├── package-lock.json      - Locked dependency versions
├── tsconfig.json          - Base TypeScript configuration
├── tsconfig.writer.json   - Writer app TypeScript config
├── node_modules/          - NPM dependencies (gitignored)
└── README.md              - This file
```

## Purpose

This directory consolidates all frontend build tooling to keep the project root clean.

## Usage

### Build TypeScript

```bash
# From project root
cd frontend && npm run build:writer

# Or from frontend directory
npm run build:writer
```

### Install Dependencies

```bash
cd frontend
npm install
```

### Available Scripts

- `npm run build` - Build all TypeScript
- `npm run build:writer` - Build writer app TypeScript only
- `npm run build:scholar` - Build scholar app TypeScript only
- `npm run type-check` - Type check without emitting files
- `npm run lint` - Lint TypeScript files
- `npm run format` - Format TypeScript files with Prettier

## TypeScript Source Locations

- **Writer App:** `../apps/writer_app/static/writer_app/ts/`
- **Scholar App:** `../static/ts/scholar/`
- **Shared Utils:** `../static/ts/types/`, `../static/ts/utils/`

## Build Output Locations

- **Writer App:** `../apps/writer_app/static/writer_app/js/`
- **Scholar App:** `../apps/scholar_app/static/scholar_app/js/`

## Notes

- All paths in tsconfig files are relative to this `frontend/` directory
- Build is automatically called during Docker builds (see `deployment/docker/*/Makefile`)
- Node modules are gitignored to avoid bloat

---

**Last Updated:** 2025-11-03
