# Deployment Guide

Deploy POC Accelerator to production.

## Local Development

```bash
python app.py
# Runs on http://localhost:5000
```

## Docker

```bash
docker build -t poc-accelerator .
docker run -p 5000:5000 poc-accelerator
```

## Azure Container Apps

```bash
az containerapp create \
  --name poc-accelerator \
  --image derricksobrien/poc-accelerator:latest \
  --environment myenv \
  --target-port 5000
```

## GitHub Pages (Documentation)

Already deployed:
```
https://derricksobrien.github.io/poc-accelerator/
```

---

## Next Steps

- [Getting Started](getting-started.html) - Quick start guide
- [API Reference](api-reference.html) - REST endpoints
- [Back to Home](index.html) - Return to documentation

---

[View on GitHub](https://github.com/derricksobrien/poc-accelerator)
