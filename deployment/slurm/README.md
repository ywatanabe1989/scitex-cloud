<!-- ---
!-- Timestamp: 2025-11-26 23:45:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/deployment/slurm/README.md
!-- --- -->

# SLURM

Host runs SLURM. Docker connects to it.

## Install (once)

```bash
sudo ./install-host.sh
make env=dev rebuild
```

## Fix Problems

```bash
sudo ./fix.sh
```

## Check Status

```bash
make env=dev status
```

<!-- EOF -->