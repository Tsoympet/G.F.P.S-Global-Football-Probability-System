# Release Instructions

This document explains how to trigger the release workflow for GFPS Desktop.

## Automatic Trigger via Git Tag

The `release.yml` workflow is configured to run automatically when a version tag is pushed to the repository.

### Creating a Release

1. **Ensure the version is updated** in both:
   - `GFPS/desktop/package.json`
   - `GFPS/desktop/src-tauri/tauri.conf.json`

2. **Create and push a git tag** matching the version:
   ```bash
   # For stable releases (e.g., v1.0.0, v0.1.0)
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   
   # For beta releases (e.g., v1.0.0-beta.1)
   git tag -a v1.0.0-beta.1 -m "Beta release 1.0.0-beta.1"
   git push origin v1.0.0-beta.1
   ```

3. **The workflow will automatically**:
   - Determine the release channel (stable or beta) from the tag format
   - Build release notes from commits since the last tag
   - Set up Node.js and Rust environments
   - Install dependencies
   - Build the Tauri desktop application
   - Create installers for Windows (MSI), macOS (DMG), and Linux (AppImage)
   - Create a GitHub release with the built artifacts

## Manual Trigger via GitHub UI

Alternatively, you can manually trigger the workflow:

1. Go to the repository on GitHub
2. Navigate to **Actions** → **Release Desktop**
3. Click **Run workflow**
4. Select the branch and click **Run workflow**

**Note**: When using manual trigger, the workflow will use `GITHUB_REF_NAME` which should be a tag. For proper releases, it's recommended to use the git tag method above.

## Release Tag Formats

- **Stable releases**: `v{major}.{minor}.{patch}` (e.g., `v1.0.0`, `v0.1.0`)
  - Marked as latest release
  - Intended for all users
  
- **Beta releases**: `v{major}.{minor}.{patch}-beta.{number}` (e.g., `v1.0.0-beta.1`)
  - Marked as pre-release
  - Contains experimental features

## Current Tag

A tag `v0.1.0` has been created for the initial release. To push it and trigger the workflow:

```bash
git push origin v0.1.0
```

This will start the release workflow automatically.
