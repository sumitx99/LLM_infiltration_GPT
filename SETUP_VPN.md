# PIA VPN Setup Guide

This guide will help you set up Private Internet Access (PIA) VPN for use with the ChatGPT automation script.

## Prerequisites
- PIA VPN subscription (you already have this!)
- Windows 10/11 system
- Administrator privileges

## Step 1: Install PIA VPN Client

1. **Download PIA Desktop App:**
   - Go to https://www.privateinternetaccess.com/download
   - Download the Windows client
   - Install the application

2. **Login to PIA:**
   - Open the PIA app
   - Login with your credentials:
     - Username: `p8551263`
     - Password: `Eoxs12345!`

## Step 2: Install PIA CLI Tool (piactl)

The script uses the command-line interface to control PIA programmatically.

1. **Enable Command Line Interface:**
   - Open PIA desktop app
   - Go to Settings → General
   - Enable "Allow LAN Traffic" (recommended)
   - Enable "PIA CLI" or "Command Line Interface" if available

2. **Install piactl separately (if not included):**
   - Download from: https://github.com/pia-foss/desktop/releases
   - Look for CLI tools or check PIA installation directory:
     - `C:\Program Files\Private Internet Access\`
     - `C:\Users\[Username]\AppData\Local\Programs\Private Internet Access\`

3. **Add to PATH (Windows):**
   ```cmd
   # Add PIA installation directory to your PATH
   # Usually: C:\Program Files\Private Internet Access\
   ```

## Step 3: Test PIA CLI

Open Command Prompt or PowerShell and test:

```cmd
# Check if piactl is available
piactl --version

# Login (if not already logged in)
piactl login p8551263

# Test connection
piactl connect --region us-east
piactl status
piactl disconnect
```

## Step 4: Test with Our Script

Run the VPN test script:

```cmd
python test_pia_vpn.py
```

Choose option 2 for a quick test.

## Troubleshooting

### piactl not found
- Ensure PIA is installed properly
- Check if CLI is enabled in PIA settings
- Add PIA directory to PATH environment variable

### Connection fails
- Make sure you're logged into PIA desktop app first
- Try connecting manually through the app
- Check your internet connection
- Verify credentials are correct

### Permission errors
- Run Command Prompt as Administrator
- Ensure PIA service is running

## Alternative: Manual OpenVPN Setup

If piactl doesn't work, you can use OpenVPN:

1. **Download OpenVPN configs from PIA:**
   - Login to PIA website
   - Download OpenVPN configuration files
   - Extract to a folder

2. **Install OpenVPN:**
   - Download from https://openvpn.net/community-downloads/
   - Install OpenVPN client

3. **Modify script to use OpenVPN:**
   - The script can be adapted to use `openvpn` command instead of `piactl`

## Configuration Files

Your VPN settings are in `vpn_config.json`:

```json
{
    "vpn_provider": "pia",
    "credentials": {
        "username": "p8551263",
        "password": "Eoxs12345!"
    },
    "settings": {
        "auto_rotate": true,
        "rotation_interval": 5,
        "preferred_countries": ["us", "uk", "ca", "de", "fr", "jp", "au", "nl"]
    }
}
```

## Usage

Once set up, the main script (`main.py`) will:

1. **Auto-connect** to a random country at startup
2. **Rotate VPN** every 5 prompts (configurable)
3. **Verify connections** by checking IP changes
4. **Auto-disconnect** when script ends

## Security Notes

- Keep your credentials secure
- Consider using environment variables instead of hardcoded passwords
- Monitor your VPN usage through PIA dashboard
- The script logs VPN location with each prompt for tracking

## Support

If you encounter issues:
1. Check PIA desktop app works manually first
2. Verify CLI tools are installed
3. Test with `test_pia_vpn.py` script
4. Check Windows firewall settings
5. Contact PIA support if needed 