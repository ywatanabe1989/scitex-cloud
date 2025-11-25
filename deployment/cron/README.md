# SciTeX Cron Jobs

## ⚠️ DEPRECATED: Visitor Pool Reset (23:59 Daily Reset)

**Status:** DEPRECATED - No longer used as of 2025-11

The visitor pool system now uses **60-minute sessions with automatic expiration**, eliminating the need for daily 23:59 resets.

### New System (Current)

- ✅ Visitors get 60-minute sessions
- ✅ Sessions automatically expire after 60 minutes of inactivity
- ✅ Slots freed immediately on signup or timeout
- ✅ No cron job needed - handled by session middleware
- ✅ Data automatically migrated on signup

### Old System (Deprecated)

The following setup is **no longer used**:

- ❌ Daily reset at 23:59
- ❌ Manual cron job configuration
- ❌ `reset_visitor_pool.sh` script

If you need to manually clean up expired sessions for testing:

```bash
python manage.py shell
>>> from apps.public_app.visitor_pool import VisitorPool
>>> VisitorPool.free_expired_allocations()
```

### Migration Notes

If you previously had the cron job installed:

1. Remove from host crontab:
```bash
crontab -e
# Remove line: 59 23 * * * /path/to/reset_visitor_pool.sh
```

2. The cron package is still included in Docker for potential future use, but no cron jobs are currently configured.
