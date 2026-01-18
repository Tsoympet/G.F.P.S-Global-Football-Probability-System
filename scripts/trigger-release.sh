#!/bin/bash

# Script to trigger the release workflow for GFPS Desktop
# This script creates and pushes a version tag to trigger the automated release

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the version from package.json
PACKAGE_JSON="GFPS/desktop/package.json"
TAURI_CONF="GFPS/desktop/src-tauri/tauri.conf.json"

if [ ! -f "$PACKAGE_JSON" ]; then
    echo -e "${RED}Error: $PACKAGE_JSON not found${NC}"
    exit 1
fi

# Extract version from package.json
VERSION=$(grep '"version"' "$PACKAGE_JSON" | head -1 | sed 's/.*"version": "\(.*\)".*/\1/')

if [ -z "$VERSION" ]; then
    echo -e "${RED}Error: Could not extract version from $PACKAGE_JSON${NC}"
    exit 1
fi

# Verify version in tauri.conf.json matches
TAURI_VERSION=$(grep '"version"' "$TAURI_CONF" | head -1 | sed 's/.*"version": "\(.*\)".*/\1/')

if [ "$VERSION" != "$TAURI_VERSION" ]; then
    echo -e "${RED}Error: Version mismatch!${NC}"
    echo -e "  package.json: $VERSION"
    echo -e "  tauri.conf.json: $TAURI_VERSION"
    exit 1
fi

# Determine release type
RELEASE_TYPE="stable"
TAG_NAME="v${VERSION}"

if [[ "$VERSION" =~ -beta\. ]]; then
    RELEASE_TYPE="beta"
fi

echo -e "${GREEN}Release Configuration:${NC}"
echo -e "  Version: $VERSION"
echo -e "  Tag: $TAG_NAME"
echo -e "  Type: $RELEASE_TYPE"
echo ""

# Check if tag already exists
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Tag $TAG_NAME already exists locally${NC}"
    read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "$TAG_NAME"
        echo -e "${GREEN}Deleted existing local tag${NC}"
    else
        echo -e "${RED}Aborted${NC}"
        exit 1
    fi
fi

# Create the tag
echo -e "${GREEN}Creating tag $TAG_NAME...${NC}"
git tag -a "$TAG_NAME" -m "Release version $VERSION"

# Confirm before pushing
echo ""
echo -e "${YELLOW}This will push the tag and trigger the release workflow.${NC}"
echo -e "The workflow will:"
echo -e "  1. Build the desktop application"
echo -e "  2. Create installers (MSI, DMG, AppImage)"
echo -e "  3. Create a GitHub release with artifacts"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Tag created but not pushed. You can push it later with:${NC}"
    echo -e "  git push origin $TAG_NAME"
    exit 0
fi

# Push the tag
echo -e "${GREEN}Pushing tag to origin...${NC}"
git push origin "$TAG_NAME"

echo ""
echo -e "${GREEN}✓ Release triggered successfully!${NC}"
echo -e "  Tag: $TAG_NAME"
echo -e "  Monitor progress at: https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/actions"
