#!/bin/bash
# Script to create a new GFPS Desktop release
# Usage: ./scripts/create_release.sh <version>
# Example: ./scripts/create_release.sh 0.1.0

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 0.1.0"
  echo "Example: $0 1.0.0-beta.1"
  exit 1
fi

VERSION="$1"
TAG="v${VERSION}"

# Validate version format
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-beta\.[0-9]+)?$ ]]; then
  echo "❌ Invalid version format: $VERSION"
  echo "   Expected format: X.Y.Z or X.Y.Z-beta.N"
  exit 1
fi

echo "🔍 Checking version consistency..."

# Check package.json version
PKG_VERSION=$(grep '"version"' GFPS/desktop/package.json | head -1 | sed 's/.*: "\(.*\)",/\1/')
if [ "$PKG_VERSION" != "$VERSION" ]; then
  echo "❌ Version mismatch in GFPS/desktop/package.json"
  echo "   Expected: $VERSION"
  echo "   Found: $PKG_VERSION"
  exit 1
fi

# Check tauri.conf.json version
TAURI_VERSION=$(grep '"version"' GFPS/desktop/src-tauri/tauri.conf.json | head -1 | sed 's/.*: "\(.*\)",/\1/')
if [ "$TAURI_VERSION" != "$VERSION" ]; then
  echo "❌ Version mismatch in GFPS/desktop/src-tauri/tauri.conf.json"
  echo "   Expected: $VERSION"
  echo "   Found: $TAURI_VERSION"
  exit 1
fi

# Check Cargo.toml version
CARGO_VERSION=$(grep '^version = ' GFPS/desktop/src-tauri/Cargo.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
if [ "$CARGO_VERSION" != "$VERSION" ]; then
  echo "❌ Version mismatch in GFPS/desktop/src-tauri/Cargo.toml"
  echo "   Expected: $VERSION"
  echo "   Found: $CARGO_VERSION"
  exit 1
fi

echo "✅ All versions are consistent: $VERSION"
echo ""

# Check if tag already exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "❌ Tag $TAG already exists"
  exit 1
fi

echo "📝 Creating release tag: $TAG"
git tag -a "$TAG" -m "Release version $VERSION"

echo ""
echo "✅ Tag created successfully!"
echo ""
echo "To trigger the release workflow, push the tag:"
echo "  git push origin $TAG"
echo ""
echo "This will:"
echo "  1. Build installers for Windows (MSI), macOS (DMG), and Linux (AppImage)"
echo "  2. Create a GitHub release with all installers attached"
echo "  3. Generate release notes from commits since the last tag"
if [[ "$VERSION" =~ -beta\. ]]; then
  echo "  4. Mark the release as pre-release (beta)"
else
  echo "  4. Mark the release as the latest stable release"
fi
