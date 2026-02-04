# Setting Up GitHub Pages for POC Accelerator Documentation

**Complete guide to deploy documentation to GitHub Pages**

---

## Overview

Your documentation will be hosted at:
```
https://your-github-username.github.io/poc-accelerator/
```

---

## Prerequisites

- GitHub account
- Repository access
- Git installed locally

---

## Option 1: Using Jekyll (Recommended)

### Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com/new)
2. Create new repository: `poc-accelerator`
3. Clone to your local machine:
```bash
git clone https://github.com/your-username/poc-accelerator.git
cd poc-accelerator
```

### Step 2: Copy Files to Repository

```bash
# Copy the entire project
cp -r /path/to/TechConnect/* ./
```

### Step 3: Initialize Git and Commit

```bash
git add .
git commit -m "Initial commit: POC Accelerator RAG system with documentation"
git push origin main
```

### Step 4: Configure GitHub Pages

1. Go to **Settings** → **Pages**
2. Under "Source", select **main branch**
3. Under "Folder", select **/docs**
4. Click **Save**

### Step 5: Enable GitHub Pages

Wait 1-2 minutes for GitHub to build your site.

Your documentation is now live at:
```
https://your-username.github.io/poc-accelerator/
```

---

## Option 2: Using HTML Documentation Site

If you prefer a simpler approach with the custom HTML interface:

### Step 1: Create Repository

Same as Option 1, Step 1-2

### Step 2: Copy HTML Documentation

The `docs/index.html` file is a self-contained documentation site.

### Step 3: Commit and Push

```bash
git add docs/index.html
git commit -m "Add HTML documentation site"
git push origin main
```

### Step 4: Enable GitHub Pages

1. Settings → Pages
2. Source: **main branch**
3. Folder: **/docs**
4. Save

Your site is now available at:
```
https://your-username.github.io/poc-accelerator/
```

---

## Option 3: Using GitHub Wiki

Alternative simple approach:

### Step 1: Enable Wiki

1. Repository Settings
2. Check "Wikis" under Features
3. Click **Create the first page**

### Step 2: Create Pages

Create wiki pages for:
- Home
- Getting Started
- Setup Guide
- Deployment
- API Reference
- Architecture
- Troubleshooting

### Step 3: Link Navigation

Each page can link to others. Wiki pages auto-generate a sidebar.

---

## Customizing Your Site

### Update `_config.yml`

Edit `docs/_config.yml`:

```yaml
title: POC Accelerator RAG System
description: Complete Documentation
url: "https://your-username.github.io/poc-accelerator"
baseurl: "/poc-accelerator"
```

Replace `your-username` with your GitHub username.

### Add Custom Domain (Optional)

To use your own domain (e.g., `docs.example.com`):

1. Settings → Pages
2. Under "Custom domain", enter your domain
3. Add DNS records to your domain registrar:
   ```
   Type: CNAME
   Name: www
   Value: your-username.github.io
   ```

---

## Jekyll Setup (Local Testing)

Test your site locally before pushing:

### Install Jekyll

```bash
gem install bundler jekyll
```

### Create Gemfile

In `docs/` directory, create `Gemfile`:

```ruby
source "https://rubygems.org"
gem "github-pages", group: :jekyll_plugins
gem "jekyll-theme-cayman"
```

### Install Dependencies

```bash
cd docs
bundle install
```

### Serve Locally

```bash
bundle exec jekyll serve
```

Visit: `http://localhost:4000/poc-accelerator/`

---

## File Structure for GitHub Pages

```
poc-accelerator/
├── docs/
│   ├── _config.yml           ← Jekyll configuration
│   ├── index.md              ← Home page
│   ├── index.html            ← Custom HTML documentation (alternative)
│   ├── getting-started.md
│   ├── setup-guide.md
│   ├── deployment.md
│   ├── api-reference.md
│   ├── architecture.md
│   ├── _layouts/             ← Custom layouts (optional)
│   │   └── default.html
│   └── assets/               ← Custom CSS/JS (optional)
│       └── css/
│           └── style.css
├── TechConnect/              ← Main application
│   ├── app.py
│   ├── rag_system.py
│   └── ...
└── README.md
```

---

## Deployment Checklist

- [ ] Repository created on GitHub
- [ ] Files pushed to `main` branch
- [ ] `/docs` folder exists
- [ ] `_config.yml` configured
- [ ] GitHub Pages enabled in Settings
- [ ] Custom domain configured (optional)
- [ ] Site builds successfully
- [ ] Documentation accessible via URL
- [ ] Navigation links working
- [ ] Mobile responsive

---

## CI/CD Integration (Optional)

Automatically rebuild documentation on commits:

### Create `.github/workflows/build-docs.yml`

```yaml
name: Build Documentation

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - '.github/workflows/build-docs.yml'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Jekyll site
        uses: helaili/jekyll-action@v2
        with:
          target_branch: gh-pages
          build_dir: docs
```

---

## Monitoring

### Check Build Status

1. Go to repository **Actions** tab
2. See build history
3. Check for errors in build logs

### View Site Analytics

1. Settings → Pages
2. Scroll to "GitHub Pages Analytics"
3. View traffic data

---

## Troubleshooting

### Site Not Building

**Problem**: GitHub Pages build fails

**Solution**:
1. Check Actions tab for errors
2. Verify `_config.yml` syntax
3. Check for conflicting Jekyll plugins
4. Commit `Gemfile.lock` if using bundler

### Old Content Showing

**Problem**: Changes not reflected

**Solution**:
1. Hard refresh browser (Ctrl+Shift+R)
2. Clear browser cache
3. Wait 5 minutes for GitHub Pages rebuild
4. Check Actions tab for build errors

### Custom Domain Issues

**Problem**: Domain not working

**Solution**:
1. Verify DNS records
2. Wait up to 24 hours for DNS propagation
3. Check SSL certificate status
4. Verify domain in GitHub settings

### Theme Not Applying

**Problem**: Theme from `_config.yml` not showing

**Solution**:
1. Ensure `theme: jekyll-theme-cayman` in `_config.yml`
2. Run `bundle update` locally
3. Test with `bundle exec jekyll serve`
4. Commit and push

---

## Additional Resources

- **Jekyll Documentation**: https://jekyllrb.com/docs/
- **GitHub Pages Help**: https://docs.github.com/en/pages
- **Jekyll Themes**: https://pages.github.com/themes/
- **Markdown Guide**: https://www.markdownguide.org/

---

## Best Practices

### Documentation

- Keep documentation updated with code
- Use consistent formatting
- Include code examples
- Link between related docs
- Add table of contents for long pages

### Site Maintenance

- Monitor build status regularly
- Review site analytics
- Update dependencies periodically
- Test changes locally before pushing
- Keep backup of documentation

### User Experience

- Clear navigation structure
- Fast page load times
- Mobile responsive design
- Search functionality
- Accessibility (WCAG 2.1)

---

## Next Steps

1. Create GitHub repository
2. Push code and documentation
3. Enable GitHub Pages
4. Test site functionality
5. Share documentation URL with team
6. Monitor analytics

---

**Your documentation site is now ready for the world to see!** 🌐
