# GitHub Pages Deployment Script for POC Accelerator

**Automated setup and deployment of documentation to GitHub Pages**

---

## Windows Batch Script

Create `deploy-docs.bat`:

```batch
@echo off
REM POC Accelerator - GitHub Pages Documentation Deployment
REM This script prepares and deploys documentation to GitHub Pages

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║    POC Accelerator - GitHub Pages Deployment           ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Configuration
set GITHUB_USERNAME=your-github-username
set REPO_NAME=poc-accelerator
set DOCS_DIR=docs
set REPO_URL=https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
set GITHUB_IO_URL=https://%GITHUB_USERNAME%.github.io/%REPO_NAME%/

REM Check if Git is installed
echo [1/6] Checking prerequisites...
git --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Git not found. Please install Git.
    pause
    exit /b 1
)
echo ✓ Git found

REM Check if documentation directory exists
if not exist "%DOCS_DIR%" (
    echo ✗ Documentation directory not found: %DOCS_DIR%
    pause
    exit /b 1
)
echo ✓ Documentation directory found

REM Initialize Git (if needed)
echo.
echo [2/6] Initializing Git repository...
if not exist ".git" (
    git init
    echo ✓ Git repository initialized
) else (
    echo ✓ Git repository already exists
)

REM Configure Git
echo.
echo [3/6] Configuring Git...
git config --global user.name "POC Accelerator Bot"
git config --global user.email "your-email@example.com"
echo ✓ Git configured

REM Add and commit documentation
echo.
echo [4/6] Committing documentation...
git add %DOCS_DIR%
git add *.md
git commit -m "Update documentation for GitHub Pages" || echo ✓ No changes to commit
echo ✓ Documentation committed

REM Add remote (if needed)
echo.
echo [5/6] Configuring remote repository...
git remote add origin %REPO_URL% 2>nul
git remote set-url origin %REPO_URL%
echo ✓ Remote configured

REM Push to GitHub
echo.
echo [6/6] Pushing to GitHub...
git push -u origin main
if errorlevel 1 (
    echo ✗ Failed to push. Check your GitHub credentials.
    pause
    exit /b 1
)
echo ✓ Documentation pushed successfully

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║         Deployment Complete!                           ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Your documentation is now available at:
echo %GITHUB_IO_URL%
echo.
echo Next steps:
echo 1. Go to GitHub repository: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo 2. Enable GitHub Pages in Settings ^> Pages
echo 3. Select 'main' branch and '/docs' folder
echo 4. Wait 1-2 minutes for site to build
echo.
pause
```

---

## Bash Script

Create `deploy-docs.sh`:

```bash
#!/bin/bash

# POC Accelerator - GitHub Pages Documentation Deployment
# This script prepares and deploys documentation to GitHub Pages

set -e

# Configuration
GITHUB_USERNAME="your-github-username"
REPO_NAME="poc-accelerator"
DOCS_DIR="docs"
REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
GITHUB_IO_URL="https://$GITHUB_USERNAME.github.io/$REPO_NAME/"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    POC Accelerator - GitHub Pages Deployment           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ Git not found. Please install Git.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Git found${NC}"

if [ ! -d "$DOCS_DIR" ]; then
    echo -e "${RED}✗ Documentation directory not found: $DOCS_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Documentation directory found${NC}"

# Step 2: Initialize Git
echo
echo -e "${YELLOW}[2/6] Initializing Git repository...${NC}"
if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${GREEN}✓ Git repository already exists${NC}"
fi

# Step 3: Configure Git
echo
echo -e "${YELLOW}[3/6] Configuring Git...${NC}"
git config --global user.name "POC Accelerator Bot" || true
git config --global user.email "your-email@example.com" || true
echo -e "${GREEN}✓ Git configured${NC}"

# Step 4: Add and commit
echo
echo -e "${YELLOW}[4/6] Committing documentation...${NC}"
git add "$DOCS_DIR"
git add *.md
git commit -m "Update documentation for GitHub Pages" || echo -e "${GREEN}✓ No changes to commit${NC}"
echo -e "${GREEN}✓ Documentation committed${NC}"

# Step 5: Configure remote
echo
echo -e "${YELLOW}[5/6] Configuring remote repository...${NC}"
git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
echo -e "${GREEN}✓ Remote configured${NC}"

# Step 6: Push to GitHub
echo
echo -e "${YELLOW}[6/6] Pushing to GitHub...${NC}"
git push -u origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to push. Check your GitHub credentials.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Documentation pushed successfully${NC}"

echo
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Deployment Complete!                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${GREEN}Your documentation is now available at:${NC}"
echo "$GITHUB_IO_URL"
echo
echo -e "${GREEN}Next steps:${NC}"
echo "1. Go to GitHub repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "2. Enable GitHub Pages in Settings > Pages"
echo "3. Select 'main' branch and '/docs' folder"
echo "4. Wait 1-2 minutes for site to build"
echo
```

---

## Usage Instructions

### Windows

1. **Update Script Variables**
   ```batch
   set GITHUB_USERNAME=your-actual-github-username
   ```

2. **Run Script**
   ```bash
   deploy-docs.bat
   ```

### Linux/macOS

1. **Update Script Variables**
   ```bash
   GITHUB_USERNAME="your-actual-github-username"
   ```

2. **Make Executable**
   ```bash
   chmod +x deploy-docs.sh
   ```

3. **Run Script**
   ```bash
   ./deploy-docs.sh
   ```

---

## Manual Deployment Steps

If you prefer manual control:

```bash
# 1. Initialize Git
git init

# 2. Configure user
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 3. Add files
git add docs/
git add *.md

# 4. Commit
git commit -m "Initial documentation for GitHub Pages"

# 5. Add remote
git remote add origin https://github.com/your-username/poc-accelerator.git

# 6. Push to GitHub
git push -u origin main
```

---

## Post-Deployment

After running the deployment script:

### Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (gear icon)
3. Scroll to **Pages** section
4. Under "Source", select **main** branch
5. Under "Folder", select **/docs**
6. Click **Save**

### Wait for Build

GitHub will automatically build your site:
- Check **Actions** tab to see build progress
- Wait 1-2 minutes for completion
- Site will be available at: `https://username.github.io/poc-accelerator/`

### Custom Domain (Optional)

1. In GitHub Pages settings, enter your custom domain
2. Add DNS CNAME record to your domain registrar
3. GitHub will handle SSL certificate automatically

---

## Troubleshooting

### Authentication Failed

**Error**: "fatal: Authentication failed"

**Solution**:
- Use personal access token instead of password
- Create token at: https://github.com/settings/tokens
- Use token as password when prompted

### Repository Not Found

**Error**: "Repository not found"

**Solution**:
- Verify repository name is correct
- Check GitHub username spelling
- Ensure repository exists on GitHub

### Site Not Building

**Error**: GitHub Pages shows build error

**Solution**:
- Check Actions tab for detailed error
- Verify `_config.yml` syntax
- Ensure files are in `/docs` folder
- Check for Jekyll version conflicts

### Slow Deployment

**Issue**: GitHub Pages takes a long time to build

**Reason**: Normal behavior - can take 1-5 minutes

**Solution**:
- Be patient, don't push multiple times
- Check Actions tab for current status
- Clear browser cache if needed

---

## Continuous Deployment

### GitHub Actions Workflow

Create `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy Documentation

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - '*.md'
      - '.github/workflows/deploy-docs.yml'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build site
        run: |
          if [ -f "Gemfile" ]; then
            bundle install
            bundle exec jekyll build
          fi
      - name: Deploy to GitHub Pages
        uses: actions/upload-artifact@v3
        with:
          name: site
          path: docs/
```

---

## Verification Checklist

- [ ] Script customized with correct GitHub username
- [ ] Documentation files exist in `/docs` folder
- [ ] Git repository initialized
- [ ] Remote repository configured
- [ ] Changes pushed to GitHub
- [ ] GitHub Pages enabled in repository settings
- [ ] Source branch set to `main`
- [ ] Source folder set to `/docs`
- [ ] Site builds successfully (check Actions)
- [ ] Site accessible at GitHub Pages URL
- [ ] Navigation links working
- [ ] Mobile responsive layout working

---

## Next Steps

1. Run deployment script
2. Enable GitHub Pages in repository settings
3. Wait for build completion
4. Share documentation URL with team
5. Monitor analytics in GitHub Pages settings
6. Update documentation as needed

---

**Your documentation site will be live within 2-5 minutes!** 🚀
