#!/bin/bash

# Script to create a release tag for PyPI deployment
# This script helps when organization rules prevent automated tag creation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏷️  PyPI Release Tag Creator${NC}"
echo "=================================="

# Get current version from pyproject.toml
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Error: pyproject.toml not found${NC}"
    exit 1
fi

CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
if [ -z "$CURRENT_VERSION" ]; then
    echo -e "${RED}❌ Error: Could not extract version from pyproject.toml${NC}"
    exit 1
fi

TAG_NAME="v${CURRENT_VERSION}"

echo -e "${BLUE}📦 Current version:${NC} ${CURRENT_VERSION}"
echo -e "${BLUE}🏷️  Tag to create:${NC} ${TAG_NAME}"
echo

# Check if tag already exists
if git tag -l | grep -q "^${TAG_NAME}$"; then
    echo -e "${YELLOW}⚠️  Tag ${TAG_NAME} already exists locally${NC}"
    echo -e "${YELLOW}   Do you want to delete and recreate it? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        git tag -d "${TAG_NAME}"
        echo -e "${GREEN}✅ Local tag deleted${NC}"
    else
        echo -e "${YELLOW}⏭️  Skipping tag creation${NC}"
        exit 0
    fi
fi

# Check if tag exists on remote
if git ls-remote --tags origin | grep -q "refs/tags/${TAG_NAME}$"; then
    echo -e "${YELLOW}⚠️  Tag ${TAG_NAME} already exists on remote${NC}"
    echo -e "${YELLOW}   Do you want to delete and recreate it? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        git push origin ":refs/tags/${TAG_NAME}" || {
            echo -e "${RED}❌ Failed to delete remote tag. You may not have permissions.${NC}"
            echo -e "${YELLOW}💡 Try using GitHub web interface to delete the tag${NC}"
            exit 1
        }
        echo -e "${GREEN}✅ Remote tag deleted${NC}"
    else
        echo -e "${YELLOW}⏭️  Skipping tag creation${NC}"
        exit 0
    fi
fi

# Create and push the tag
echo -e "${BLUE}🔨 Creating tag ${TAG_NAME}...${NC}"
git tag -a "${TAG_NAME}" -m "Release ${TAG_NAME}"

echo -e "${BLUE}📤 Pushing tag to remote...${NC}"
if git push origin "${TAG_NAME}"; then
    echo -e "${GREEN}✅ Tag ${TAG_NAME} created and pushed successfully!${NC}"
    echo
    echo -e "${BLUE}🚀 Next steps:${NC}"
    echo "1. Go to GitHub Actions → Deploy to PyPI"
    echo "2. Click 'Run workflow'"
    echo "3. Set 'Create git tag' to false (tag already exists)"
    echo "4. Click 'Run workflow' to deploy to PyPI"
    echo
    echo -e "${BLUE}🔗 GitHub Actions:${NC} https://github.com/grasp-labs/ds-event-stream-py-sdk/actions/workflows/deploy-pypi.yml"
else
    echo -e "${RED}❌ Failed to push tag. You may not have push permissions.${NC}"
    echo -e "${YELLOW}💡 Alternative approaches:${NC}"
    echo "1. Ask a repository admin to create the tag"
    echo "2. Use GitHub web interface to create a release (which creates the tag)"
    echo "3. Run the PyPI deployment without tag creation"
    exit 1
fi
