# Python Virtual Environment Guide

## Why use virtual environments?

Virtual environments prevent dependency conflicts between projects.

Each project can have its own package versions without affecting other projects.

## Create a virtual environment

```bash
python3 -m venv venv
```

This creates a folder named venv.

## Activate environment

```bash
source venv/bin/activate
```

Terminal prompt will show:

```bash
(venv)
```

## Install dependencies

```bash
pip install requests flask sqlalchemy
```

## Save installed packages

```bash
pip freeze > requirements.txt
```

## Install packages from requirements file

```bash
pip install -r requirements.txt
```

## Check installed packages

```bash
pip list
```

## Deactivate environment

```bash
deactivate
```

## Best Practices

- Create one venv per project
- Add venv/ to .gitignore
- Keep requirements.txt updated
- Never commit venv folder to Git