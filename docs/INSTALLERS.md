# Desktop Application Installers

This document provides detailed information about GFPS Desktop application installers for end users.

## Download

Pre-built installers are available from the [GitHub Releases page](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/releases).

Each release includes installers for:
- **Windows** (`.msi`)
- **macOS** (`.dmg`)
- **Linux** (`.AppImage`)

## Installation Instructions

### Windows

1. Download the `.msi` installer from the latest release
2. Double-click the installer file to launch the installation wizard
3. Follow the on-screen instructions
4. **Security Warning**: Windows may show a SmartScreen warning for unsigned applications
   - Click "More info"
   - Click "Run anyway"
5. The application will be installed to `C:\Program Files\GFPS Desktop`
6. Launch from the Start Menu or desktop shortcut

**System Requirements:**
- Windows 10 or later (64-bit)
- At least 200 MB of free disk space

### macOS

1. Download the `.dmg` file from the latest release
2. Double-click the downloaded file to mount the disk image
3. Drag the GFPS app to your Applications folder
4. **Gatekeeper Warning**: macOS may block the app from opening (for unsigned apps)
   - Right-click the app in Applications
   - Select "Open"
   - Click "Open" in the confirmation dialog
   - This only needs to be done once
5. Launch the application from your Applications folder

**System Requirements:**
- macOS 10.15 (Catalina) or later
- Apple Silicon or Intel processor
- At least 200 MB of free disk space

### Linux

1. Download the `.AppImage` file from the latest release
2. Make the file executable:
   ```bash
   chmod +x GFPS*.AppImage
   ```
3. Run the application:
   ```bash
   ./GFPS*.AppImage
   ```
4. (Optional) Integrate with your desktop environment:
   ```bash
   # Example for Ubuntu/Debian with AppImageLauncher
   sudo apt install appimagelauncher
   # Then double-click the AppImage
   ```

**System Requirements:**
- Modern Linux distribution (Ubuntu 20.04+, Fedora 35+, etc.)
- FUSE2 or FUSE3 (usually pre-installed)
- GTK 3.24 or later
- WebKitGTK 4.1
- At least 200 MB of free disk space

**Common Linux Issues:**
- If the AppImage won't run, install FUSE:
  ```bash
  # Ubuntu/Debian
  sudo apt install libfuse2
  
  # Fedora
  sudo dnf install fuse-libs
  ```

## First Launch

When you first launch GFPS Desktop:

1. The application will open the Dashboard screen
2. **Important:** You will see a "Backend API Not Available" error because the backend server is not running
3. Follow the setup steps shown in the error banner to start the backend server
4. Once the backend is running, the dashboard will automatically connect and display data

### Starting the Backend Server

GFPS Desktop requires a local backend API server to function. Here's how to start it:

#### Quick Start (Recommended)

**Windows:**
1. Open the repository folder where you downloaded/cloned GFPS
2. Double-click `start-backend.bat`
3. Wait for the message "Uvicorn running on http://0.0.0.0:8000"

**macOS/Linux:**
1. Open Terminal
2. Navigate to the GFPS repository folder:
   ```bash
   cd path/to/G.F.P.S-Global-Football-Probability-System
   ```
3. Run the startup script:
   ```bash
   ./start-backend.sh
   ```
4. Wait for the message "Uvicorn running on http://0.0.0.0:8000"

#### Manual Setup

If the automatic scripts don't work, you can start the backend manually:

1. **Install Python 3.8 or later** from [python.org](https://www.python.org/downloads/)

2. **Install backend dependencies:**
   ```bash
   # Create virtual environment (first time only)
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r backend/requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Copy the example configuration
   cp .env.example .env
   
   # Generate a secure SECRET_KEY
   # On macOS/Linux:
   openssl rand -hex 32
   # On Windows (PowerShell):
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Edit .env and set SECRET_KEY=<generated-key>
   ```

4. **Start the backend:**
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Verify it's running:** Open http://localhost:8000/health in your browser

### After Backend is Running

1. The GFPS Desktop app will automatically connect to the backend
2. (Optional) Configure your backend API endpoint (default: `http://localhost:8000`)
3. (Optional) Sign up for a new account or log in with existing credentials
4. (Optional) Configure your data provider API keys in Settings
5. Start using the application!

## Security Considerations

### Code Signing

**Current Status**: The installers are **not code-signed** by default.

This means:
- **Windows**: SmartScreen will show a warning
- **macOS**: Gatekeeper will block the app by default
- **Linux**: No impact (AppImages don't require signing)

**Why?** Code signing requires:
- **Windows**: A code signing certificate ($100-500/year)
- **macOS**: Apple Developer account ($99/year) + notarization

For production deployments, we recommend configuring code signing certificates. See [RELEASE_INSTRUCTIONS.md](RELEASE_INSTRUCTIONS.md#code-signing-optional) for details.

### Privacy

GFPS Desktop is designed with privacy in mind:
- ✅ No telemetry or analytics
- ✅ No data collection
- ✅ All data stays local on your device
- ✅ Encrypted local storage for sensitive settings
- ✅ You control your own API keys and data providers

## Updates

GFPS Desktop does not include automatic updates. To update:

1. Check the [Releases page](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/releases) for new versions
2. Download and install the new version
3. Your settings and data will be preserved

## Uninstallation

### Windows
1. Go to Settings → Apps → Apps & features
2. Find "GFPS Desktop"
3. Click "Uninstall"

### macOS
1. Open Finder → Applications
2. Drag "GFPS" to Trash
3. Empty Trash

### Linux
Simply delete the `.AppImage` file.

**Note**: Application data is stored separately and won't be deleted:
- **Windows**: `%APPDATA%\com.gfps.desktop`
- **macOS**: `~/Library/Application Support/com.gfps.desktop`
- **Linux**: `~/.config/com.gfps.desktop`

## Troubleshooting

### Application won't start

**Windows:**
- Check Windows Event Viewer for error messages
- Try running as administrator
- Reinstall the application

**macOS:**
- Check Console app for error messages
- Make sure you followed the Gatekeeper bypass steps
- Try removing and re-adding the app from Applications

**Linux:**
- Make sure FUSE is installed
- Check file permissions
- Run from terminal to see error messages:
  ```bash
  ./GFPS*.AppImage
  ```

### Can't connect to backend

If you see "Backend API Not Available" or "Failed to fetch" errors:

1. **Verify the backend is running:**
   - Check if you started the backend server (see [Starting the Backend Server](#starting-the-backend-server))
   - The backend should show: `Uvicorn running on http://0.0.0.0:8000`
   - Visit http://localhost:8000/health in your browser - you should see `{"ok": true, ...}`

2. **Check the API endpoint configuration:**
   - Open the GFPS Desktop app
   - Go to Settings
   - Verify "API Endpoint" is set to `http://localhost:8000`
   - If you're running the backend on a different port or host, update this URL

3. **Check for port conflicts:**
   - Make sure port 8000 is not already in use
   - On Windows: `netstat -ano | findstr :8000`
   - On macOS/Linux: `lsof -i :8000` or `netstat -tuln | grep 8000`
   - If port 8000 is taken, start the backend on a different port:
     ```bash
     uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
     ```
   - Then update the API endpoint in Settings to `http://localhost:8001`

4. **Check firewall settings:**
   - Make sure your firewall allows connections to localhost:8000
   - On Windows, you may need to allow Python/uvicorn through Windows Defender Firewall

5. **Try restarting both the backend and desktop app:**
   - Stop the backend (Ctrl+C in the terminal)
   - Close the desktop app
   - Start the backend first, wait for "Uvicorn running..."
   - Then start the desktop app

6. **Check backend logs for errors:**
   - Look at the terminal where the backend is running
   - Common issues:
     - Missing SECRET_KEY in .env file
     - Database connection errors
     - Missing Python dependencies

If none of these steps work, please [open an issue](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/issues) with:
- Your operating system
- The error message you're seeing
- Backend logs from the terminal
- Desktop app version

### Settings won't save

1. Check that the application has write permissions
2. On Linux, make sure the config directory exists:
   ```bash
   mkdir -p ~/.config/com.gfps.desktop
   ```

## Release Channels

### Stable Releases

- Version format: `v1.0.0`, `v0.1.0`
- Thoroughly tested
- Recommended for all users
- Marked as "Latest" on GitHub

### Beta Releases

- Version format: `v1.0.0-beta.1`
- Early access to new features
- May contain bugs
- Marked as "Pre-release" on GitHub
- Use at your own risk

## Support

For issues and support:

1. Check the [documentation](README.md)
2. Search [existing issues](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/issues)
3. Create a [new issue](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/issues/new)

## License

GFPS Desktop is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

By installing and using this software, you agree to the [End User License Agreement (EULA)](../EULA.md).

## Disclaimer

GFPS provides probabilistic analytics, not guarantees. Football outcomes remain uncertain, and nothing in GFPS is financial advice or a promise of profit. Use responsibly and validate against your own risk tolerance.

See the [EULA](../EULA.md) for full legal disclaimers and terms of use.
