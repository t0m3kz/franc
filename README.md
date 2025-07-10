# FRANC Service Portal

[![Ruff][ruff-badge]][ruff-link]
[![Python][python-badge]][python-link]
[![Actions status][github-badge]][github-link]
[![Coverage Status][coverage-badge]][coverage-link]
[![GitHub Discussion][github-discussions-badge]][github-discussions-link]


A modern, mobile-friendly Streamlit-based network service portal for automating network operations.

## Quick Start

### Development Mode (No External Dependencies)

```bash
# Clone the repository
git clone <repository-url>
cd franc

# Install dependencies
uv sync

# Run the application
uv run streamlit run src/main.py
```

The application will start on http://localhost:8501 and work with limited functionality (no Infrahub integration).

### Full Setup with Infrahub

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Configure your Infrahub connection in `.env`:
```bash
INFRAHUB_ADDRESS=http://your-infrahub-server:8000
INFRAHUB_API_TOKEN="06438eb2-8019-4776-878c-0941b1f1d1ec"
```

3. Run the application:
```bash
uv run streamlit run src/main.py
```

## Features

- 🏢 **Data Center Deployment**: Request new DC deployments with location and design selection
- 🌐 **PoP Deployment**: Point of Presence setup with provider selection  
- 🔌 **Device Connection**: Network device connection requests with interface configuration
-  **Mobile-Friendly**: Responsive design optimized for mobile devices
- 🔍 **Built-in Help**: Contextual help and validation guidance
- 🎯 **Modern UI**: Clean, intuitive interface with real-time validation

## Architecture

- **Frontend**: Streamlit for interactive web interface
- **Backend**: Python with Infrahub SDK for network automation
- **Validation**: Comprehensive form validation with user guidance

## Documentation

- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)

## Development

```bash
# Install development dependencies
uv sync --group dev

# Run linting
uv run ruff check src/

# Run formatting  
uv run ruff format src/

# Run tests
uv run pytest
```

[ruff-badge]:
<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>
[ruff-link]:
(https://github.com/astral-sh/ruff)
[github-discussions-link]:
<https://github.com/t0m3kz/franc/discussions/>
[github-discussions-badge]:
<https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github>
[github-badge]:
<https://github.com/t0m3kz/franc/actions/workflows/main.yml/badge.svg?branch=main>
[github-link]:
<https://github.com/t0m3kz/franc/actions/workflows/main.yml>
[coverage-badge]:
https://img.shields.io/codecov/c/github/t0m3kz/franc?label=coverage
[coverage-link]:
https://codecov.io/gh/t0m3kz/franc
[python-badge]:
<https://img.shields.io/badge/python-3.10%7C3.11%7C3.12%7C3.13-000000?logo=python>
[python-link]:
<https://www.python.org>
