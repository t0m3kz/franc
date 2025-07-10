# FRANC Service Portal

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
- 📡 **Kafka Integration**: Event publishing for downstream processing
- 📱 **Mobile-Friendly**: Responsive design optimized for mobile devices
- 🔍 **Built-in Help**: Contextual help and validation guidance
- 🎯 **Modern UI**: Clean, intuitive interface with real-time validation

## Architecture

- **Frontend**: Streamlit for interactive web interface
- **Backend**: Python with Infrahub SDK for network automation
- **Messaging**: Kafka for event-driven workflows
- **Validation**: Comprehensive form validation with user guidance

## Documentation

- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)  
- [Kafka Integration](docs/kafka-integration.md)

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
