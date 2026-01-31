# Useful Commands

## Environment Setup

### First Time Setup (After Cloning)
```bash
uv sync
```

### Initialize UV Virtual Environment
```bash
uv venv venv --python=3.10
```

### Activate Virtual Environment
```bash
.venv\Scripts\activate
```

## Dependency Management

### Generate Requirements
```bash
uv pip freeze > requirements.txt
```

### Install Requirements
```bash
uv pip install -r requirements.txt
```

### Generate Requirements with pipreqs
```bash
python -m pipreqs.pipreqs C:\SRC\FinBot --encoding=utf-8 --force --ignore .venv
```

## Docker Cleanup

### Remove Unused Docker Resources
```bash
docker system prune -a --volumes -f
```

## Code Quality

### Format Code
```bash
black .
```

### Lint Code
```bash
pylint .\dash_app\
pylint .\reddit_api\
```