# Nginx HTTPS

## Setup SSL

```bash
make env=prod start
make env=prod ssl-setup
```

## Manual Certificate

```bash
docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email admin@scitex.ai \
  --agree-tos --no-eff-email \
  -d scitex.ai -d git.scitex.ai
```

## Verify

```bash
curl -I https://scitex.ai
```

## Troubleshooting

```bash
docker compose exec nginx nginx -t
docker compose logs nginx
```
