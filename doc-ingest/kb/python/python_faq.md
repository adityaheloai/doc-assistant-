# Python Frequently Asked Questions

## What is Python?

Python is a high-level, interpreted programming language known for its simple
and readable syntax. It is widely used for web development, AI/ML, automation,
data science, scripting, and backend systems.

## How do I check Python version?

```bash
python3 --version
```

## What is pip?

pip is the standard package manager for Python. It allows you to install
additional libraries and packages.

## How do I create a virtual environment?

```bash
python3 -m venv venv
```

## How do I activate a virtual environment?

On macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

## How do I install a package?

```bash
pip install package-name
```

Example:

```bash
pip install requests
```

## How do I install dependencies from requirements.txt?

```bash
pip install -r requirements.txt
```

## How do I deactivate a virtual environment?

```bash
deactivate
```

## What are Python modules?

Modules are files containing Python code that can be imported and reused
across applications.