# Production

https://scitex.ai

## Start

```bash
make env=prod start
```

## SSL Setup

```bash
cd nginx
./setup_nginx.sh
```

## Commands

```bash
make env=prod status
make env=prod logs
make env=prod restart
make env=prod db-backup
```

## Config

`SECRETS/.env.prod`
