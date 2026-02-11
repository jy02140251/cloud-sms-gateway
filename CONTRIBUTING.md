# Contributing to Cloud SMS Gateway

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/jy02140251/cloud-sms-gateway.git
cd cloud-sms-gateway
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Copy environment config:
```bash
cp .env.example .env
```

## Running Tests

```bash
pytest tests/ -v --cov=sms_gateway
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Write docstrings for all public methods
- Maximum line length: 100 characters

## Pull Request Process

1. Create a feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation if needed
5. Submit a pull request with a clear description

## Commit Message Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `chore:` Maintenance tasks