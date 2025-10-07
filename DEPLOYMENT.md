# 🚀 PyPI Deployment Guide

This guide explains how to deploy the `ds-event-stream-python-sdk` package to PyPI, especially when dealing with organization repository rules that prevent automated tag creation.

## 📋 Prerequisites

- [ ] Version updated in `pyproject.toml`
- [ ] Changes committed and pushed to `main` branch
- [ ] Access to GitHub Actions (for PyPI deployment)
- [ ] Repository admin access (for tag creation, if needed)

## 🎯 Deployment Methods

### Method 1: Automated Deployment (Recommended)

**Best for:** Repositories without strict tag creation rules

1. **Update Version** in `pyproject.toml`
2. **Commit and Push** changes to main
3. **Go to GitHub Actions** → [Deploy to PyPI](https://github.com/grasp-labs/ds-event-stream-py-sdk/actions/workflows/deploy-pypi.yml)
4. **Click "Run workflow"**
5. **Set "Create git tag"** to `true`
6. **Click "Run workflow"**

### Method 2: Manual Tag Creation (For Strict Repositories)

**Best for:** Repositories with branch protection rules that prevent automated tag creation

#### Step 1: Create Release Tag

**Option A: Using the Helper Script**
```bash
# Run the helper script
./scripts/create-release-tag.sh
```

**Option B: Manual Tag Creation**
```bash
# Get current version
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

# Create and push tag
git tag -a "v${VERSION}" -m "Release v${VERSION}"
git push origin "v${VERSION}"
```

**Option C: GitHub Web Interface**
1. Go to [Releases](https://github.com/grasp-labs/ds-event-stream-py-sdk/releases)
2. Click "Create a new release"
3. Enter tag: `v{version}` (e.g., `v0.1.1`)
4. Set target: `main`
5. Click "Create release"

#### Step 2: Deploy to PyPI

1. **Go to GitHub Actions** → [Deploy to PyPI](https://github.com/grasp-labs/ds-event-stream-py-sdk/actions/workflows/deploy-pypi.yml)
2. **Click "Run workflow"**
3. **Set "Create git tag"** to `false` (tag already exists)
4. **Click "Run workflow"**

## 🔧 Workflow Details

The PyPI deployment workflow performs these steps:

1. **✅ Get Current Version** - Extracts version from `pyproject.toml`
2. **🏷️ Handle Tag Creation** - Creates tag if requested and permitted
3. **📦 Build Package** - Creates wheel and source distributions
4. **✅ Validate Package** - Runs `twine check` for validation
5. **🚀 Publish to PyPI** - Uploads to PyPI using `PYPI_API_KEY` secret
6. **📋 Create GitHub Release** - Creates release with changelog

## 🛠️ Troubleshooting

### Tag Creation Fails

**Error:** `Cannot create ref due to creations being restricted`

**Solutions:**
1. Use Method 2 (Manual Tag Creation)
2. Ask repository admin to create the tag
3. Run deployment without tag creation

### PyPI Upload Fails

**Error:** `Invalid or non-existent authentication information`

**Solutions:**
1. Check `PYPI_API_KEY` secret is set correctly
2. Verify API key has upload permissions
3. Ensure package name is available on PyPI

### Version Already Exists

**Error:** `File already exists`

**Solutions:**
1. Bump version in `pyproject.toml`
2. Use a different version number
3. Delete existing version on PyPI (if you own it)

## 📊 Monitoring Deployment

### GitHub Actions
- **Workflow URL:** https://github.com/grasp-labs/ds-event-stream-py-sdk/actions/workflows/deploy-pypi.yml
- **Monitor progress** in real-time
- **Check logs** for detailed information

### PyPI Package
- **Package URL:** https://pypi.org/project/ds-event-stream-python-sdk/
- **Verify upload** after deployment
- **Test installation:** `pip install ds-event-stream-python-sdk`

### GitHub Releases
- **Releases URL:** https://github.com/grasp-labs/ds-event-stream-py-sdk/releases
- **Automatic release creation** with changelog
- **Download assets** and release notes

## 🎉 Post-Deployment

After successful deployment:

1. **✅ Verify PyPI Package** - Check package appears on PyPI
2. **🧪 Test Installation** - `pip install ds-event-stream-python-sdk=={version}`
3. **📋 Update Documentation** - Ensure docs reflect new version
4. **🔔 Notify Team** - Share release notes with stakeholders

## 🔐 Security Notes

- **API Keys:** Never commit PyPI API keys to repository
- **Secrets:** Use GitHub repository secrets for sensitive data
- **Permissions:** Limit deployment access to trusted maintainers
- **Verification:** Always verify package contents before deployment

---

**Need Help?** Check the [GitHub Actions logs](https://github.com/grasp-labs/ds-event-stream-py-sdk/actions) or contact the repository maintainers.
