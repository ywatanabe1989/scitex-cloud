# Feature: Windows Chrome Access to Development Server

## Request
Access the development server running in WSL from Google Chrome on Windows for a better visual experience.

## Implementation
We've implemented the following solutions:

### 1. Enhanced Start Script
The existing `start_dev.sh` script now displays the WSL IP address that can be accessed from Windows:

```bash
# Get the WSL IP address for Windows access
WSL_IP=$(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
echo "🌐 You can access the site from Windows at http://$WSL_IP:8000"
```

### 2. Windows-Specific Script
A new script `start_dev_windows.sh` has been created that:
- Starts the development server
- Prominently displays the Windows access URL
- Provides troubleshooting tips

## Usage Instructions

### Method 1: Using start_dev.sh
1. Start the development server with `./start_dev.sh`
2. Note the Windows access URL displayed in the console
3. Open Chrome in Windows and navigate to that URL

### Method 2: Using Windows-specific script
1. Run `./start_dev_windows.sh`
2. Copy the Windows access URL displayed
3. Paste it into Chrome on Windows

## Troubleshooting

If you cannot access the site from Windows:

1. **Check Windows Firewall**
   - Make sure your Windows Firewall allows connections to WSL
   - Consider temporarily disabling the firewall for testing

2. **WSL Network Reset**
   - Open PowerShell as Administrator in Windows and run:
   ```powershell
   wsl --shutdown
   ```
   - Then restart your WSL terminal and run the development server again

3. **Alternative: Port Forwarding**
   - If direct access doesn't work, set up port forwarding in Windows:
   ```powershell
   netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=(wsl hostname -I)
   ```
   - Then access via `http://localhost:8000` in Windows Chrome

## Implementation Details

The solution works by binding the Django development server to all network interfaces (0.0.0.0) instead of just localhost, making it accessible from the Windows host system via the WSL network interface.

The WSL IP address is dynamically detected when starting the server.