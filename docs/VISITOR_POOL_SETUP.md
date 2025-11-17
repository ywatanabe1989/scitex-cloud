# Visitor Pool Setup Guide

## Overview

The visitor pool allows anonymous users to try SciTeX Writer without signing up. It pre-allocates 4 visitor accounts that rotate automatically with 24-hour session expiration.

## Initial Setup (Run Once)

### 1. Create Visitor Pool

```bash
# Create 4 visitor accounts (visitor-001 to visitor-004)
python manage.py create_visitor_pool

# Or create a custom size
python manage.py create_visitor_pool --size 8
```

This creates:
- **Users**: visitor-001, visitor-002, visitor-003, visitor-004
- **Projects**: One "default-project" per visitor user
- **Filesystem**: Project directories at `/data/visitor-XXX/default-project/`

**Note**: With proper rotation and 24h session expiration, 4 slots are sufficient for development.

### 2. Verify Pool Status

```bash
python manage.py create_visitor_pool --status
```

Expected output:
```
=== Visitor Pool Status ===
Total slots: 32
Allocated: 0
Free: 32
Expired: 0
```

## How It Works

### For Anonymous Visitors

1. **Visit /writer/** → Automatically allocated a visitor slot (e.g., visitor-015)
2. **Edit & Save** → Work saved to visitor-015's project on server
3. **Sign Up** → Work transferred to their new account's default-project
4. **Slot Released** → visitor-015 slot freed for next visitor

### Session Management

Each visitor gets:
```python
session['visitor_project_id'] = 101      # Project ID
session['visitor_user_id'] = 52          # User ID of visitor-015
session['visitor_allocation_token'] = 'abc...'  # Security token
```

Session lifetime: 24 hours (configurable in `VisitorPool.SESSION_LIFETIME_HOURS`)

## Monitoring

### Check Pool Status
```bash
python manage.py create_visitor_pool --status
```

### Reset Visitor Pool (if needed)
```bash
python manage.py reset_visitor_pool
```

⚠️ **Warning**: This will clear all visitor workspaces. Only use during development.

## Troubleshooting

### Issue: "Pool Exhausted" message

**Symptom**: All 4 slots occupied
**Solution**:
1. Wait for sessions to expire (24 hours)
2. Or increase pool size: `python manage.py create_visitor_pool --size 64`

### Issue: Redirect to login page

**Symptom**: Anonymous users redirected to /auth/login/ instead of getting visitor access
**Cause**: Visitor pool not initialized
**Solution**: Run `python manage.py create_visitor_pool`

### Issue: "VisitorAllocation table not found"

**Symptom**: Fallback to old demo pool
**Solution**: Run migrations: `python manage.py migrate`

## Production Recommendations

### Pool Size

- **4 slots** (default): Good for development and testing
- **8 slots**: For light production usage (100-200 visitors/day)
- **16 slots**: For moderate usage (200-500 visitors/day)
- **32+ slots**: For heavy usage (500+ visitors/day)

**Note**: With 24h session expiration, each slot can serve ~24 visitors per day.

Calculate based on:
- Average session duration
- Expected concurrent users
- Conversion rate to signup

### Monitoring

Set up monitoring for:
```python
# Alert when pool > 80% allocated
if allocated / total > 0.8:
    send_alert("Visitor pool running low")
```

### Cleanup

Expired sessions auto-cleanup after 24 hours. No manual intervention needed.

## Architecture Details

### Database Schema

```python
VisitorAllocation:
    visitor_number: int         # 1-4 (default, configurable)
    session_key: str            # Django session key
    allocation_token: str       # Security token
    allocated_at: datetime
    expires_at: datetime
    is_active: bool
```

### Filesystem Structure

```
/data/
├── visitor-001/
│   └── default-project/
│       └── scitex/writer/...
├── visitor-002/
│   └── default-project/
│       └── scitex/writer/...
├── visitor-003/
│   └── default-project/
│       └── scitex/writer/...
└── visitor-004/
    └── default-project/
        └── scitex/writer/...
```

### On Signup Transfer

```python
# Before signup
/data/visitor-015/default-project/
    └── scitex/writer/sections/manuscript/abstract.tex

# After signup (user: alice)
/data/alice/default-project/
    └── scitex/writer/sections/manuscript/abstract.tex
```

## Console Output

When visitors access Writer, they'll see:
```javascript
[VisitorPool] ✓ Allocated: visitor-015
[VisitorPool] Project ID: 101
[VisitorPool] Project: default-project
[visitor-015] [Writer] Loading section content: manuscript/abstract
[visitor-015] [Writer] Saving 5 sections for manuscript
```

---

Last updated: 2025-11-06
