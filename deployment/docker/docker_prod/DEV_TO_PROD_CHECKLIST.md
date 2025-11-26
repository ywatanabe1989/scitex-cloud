# Production Deployment Checklist

## Before Deploy

- [ ] `SECRETS/.env.prod` updated
- [ ] `DEBUG=False`
- [ ] TypeScript compiled
- [ ] Database backed up

## Deploy

```bash
make env=prod rebuild
```

## After Deploy

- [ ] https://scitex.ai works
- [ ] https://git.scitex.ai works
- [ ] Login works
- [ ] No errors in logs

## Verify

```bash
make env=prod status
make env=prod logs
```

## Rollback

```bash
make env=prod down
# restore backup
make env=prod start
```
