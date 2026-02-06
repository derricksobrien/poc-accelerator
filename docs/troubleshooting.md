---
layout: default
title: Troubleshooting
---

# Troubleshooting

Solutions for common issues.

## Port Already in Use

```bash
# Use different port
flask run --port 5001
```

## Module Not Found

```bash
# Install dependencies
pip install -r requirements.txt
```

## Azure Authentication Failed

```bash
# Set environment variables
export OPENAI_API_KEY="your-key"
export AZURE_KEYVAULT_URL="your-url"
```

## GitHub Token Invalid

1. Generate new token: https://github.com/settings/tokens
2. Token needs: `repo`, `workflow` scopes
3. Set: `GITHUB_TOKEN` environment variable

## POC Generation is Slow

- Check internet connection
- Verify Azure API quotas
- Check system resources
- Consider caching results

## Links Not Working

- Ensure you're on the correct URL path
- Check browser cache (Ctrl+Shift+R)
- Verify .html extension in links
- Check GitHub Pages build status

---

## Next Steps

- [Getting Started](getting-started.html) - Quick start
- [Deployment Guide](deployment.html) - Deploy to production
- [Back to Home](index.html) - Return to documentation

---

[View on GitHub](https://github.com/derricksobrien/poc-accelerator)
