# Release Instructions

This document explains how to create and publish releases for GFPS Desktop.

## Quick Start

The easiest way to create a release is using the helper script:

```bash
# For stable releases (e.g., v1.0.0, v0.1.0)
./scripts/create_release.sh 0.1.0

# For beta releases (e.g., v1.0.0-beta.1)
./scripts/create_release.sh 1.0.0-beta.1

# Then push the tag to trigger the release workflow
git push origin v0.1.0
```

The script will:
- Verify version consistency across all configuration files
- Create an annotated git tag
- Provide instructions for pushing the tag

## Manual Process

If you prefer to create releases manually, follow these steps:

### 1. Update Version Numbers

Ensure the version is consistent in all three files:
- `GFPS/desktop/package.json`
- `GFPS/desktop/src-tauri/tauri.conf.json`
- `GFPS/desktop/src-tauri/Cargo.toml`

### 2. Create and Push Git Tag

```bash
# For stable releases (e.g., v1.0.0, v0.1.0)
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# For beta releases (e.g., v1.0.0-beta.1)
git tag -a v1.0.0-beta.1 -m "Beta release 1.0.0-beta.1"
git push origin v1.0.0-beta.1
```

### 3. Workflow Automation

The `release.yml` workflow will automatically:
- Detect the release channel (stable or beta) from the tag format
- Build installers on all platforms:
  - **Windows**: MSI installer
  - **macOS**: DMG disk image
  - **Linux**: AppImage executable
- Generate release notes from commits since the last tag
- Create a GitHub release with all installers attached
- Mark as pre-release for beta versions or latest for stable versions

## Release Tag Formats

- **Stable releases**: `v{major}.{minor}.{patch}` (e.g., `v1.0.0`, `v0.1.0`)
  - Marked as latest release
  - Intended for all users
  
- **Beta releases**: `v{major}.{minor}.{patch}-beta.{number}` (e.g., `v1.0.0-beta.1`)
  - Marked as pre-release
  - Contains experimental features

## Code Signing (Optional)

For production releases, you can configure code signing certificates:

### Windows Code Signing
Set the following repository secrets:
- `TAURI_SIGNING_PRIVATE_KEY`: Windows code signing certificate
- `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`: Certificate password

### macOS Code Signing
Set the following repository secrets:
- `APPLE_CERTIFICATE`: Base64-encoded signing certificate
- `APPLE_CERTIFICATE_PASSWORD`: Certificate password
- `APPLE_ID`: Apple Developer account email
- `APPLE_PASSWORD`: App-specific password
- `APPLE_TEAM_ID`: Apple Developer Team ID

**Note**: Releases without code signing will still work but may show security warnings on first launch.

## Manual Workflow Trigger

You can also trigger the release workflow manually:

1. Go to the repository on GitHub
2. Navigate to **Actions** → **Release Desktop**
3. Click **Run workflow**
4. Select a tag or branch
5. Click **Run workflow**

**Note**: For proper releases with artifacts, always use git tags as described above.

## Monitoring the Build

After pushing a tag:

1. Go to **Actions** tab in GitHub
2. Find the "Release Desktop" workflow run
3. Monitor the build progress for all platforms
4. Once complete, the release will appear in the **Releases** section

## Troubleshooting

### Version Mismatch Errors
Ensure all version numbers match in:
- `GFPS/desktop/package.json`
- `GFPS/desktop/src-tauri/tauri.conf.json`
- `GFPS/desktop/src-tauri/Cargo.toml`

### Build Failures
- Check the GitHub Actions logs for detailed error messages
- Verify all dependencies are correctly specified
- Ensure the Tauri configuration is valid

### Missing Installers
If installers are missing from the release:
- Check that the workflow completed successfully on all platforms
- Verify the `tauri.conf.json` bundle targets include: `["msi", "dmg", "appimage"]`
- Check GitHub Actions logs for upload errors

