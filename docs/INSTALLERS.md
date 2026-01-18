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

1. The application will open the Settings screen
2. Configure your backend API endpoint (default: `http://localhost:8000`)
3. (Optional) Sign up for a new account or log in with existing credentials
4. (Optional) Configure your data provider API keys
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

1. Verify the backend is running on the configured endpoint
2. Check Settings → API Endpoint
3. Try the default: `http://localhost:8000`
4. Check firewall settings

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
