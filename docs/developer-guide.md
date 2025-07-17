# FRANC - Developer Documentation

## Overview

FRANC (Streamlit connection and utilities for Infrahub) is a Streamlit-based web application that provides a service portal for network operations. This documentation covers the technical architecture, development setup, code structure, and contribution guidelines.

## Project Structure

```
franc/
├── docs/                           # Documentation
│   ├── user-guide.md              # User documentation
│   └── developer-guide.md         # This file
├── src/                           # Source code
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── help_loader.py            # Help content management utility
│   ├── infrahub.py               # Infrahub SDK integration
│   ├── schema_protocols.py       # Generated Infrahub protocols
│   ├── utils.py                  # Generic utility functions
│   ├── validation.py             # Form validation helpers
│   ├── help/                     # Help content files
│   │   ├── quick-help.md         # General help content
│   │   ├── deploy-dc.md          # Data center deployment help
│   │   ├── deploy-pop.md         # PoP deployment help
│   │   ├── connect-device.md     # Device connection help
│   │   ├── interface-config.md   # Interface configuration guide
│   │   ├── validation-tips.md    # Validation error tips
│   │   ├── *-instructions.md     # Form instruction files
│   │   └── *-next-steps.md       # Success follow-up content
│   └── services/                 # Service-specific modules
│       ├── __init__.py
│       ├── connect_device.py     # Device connection service
│       ├── deploy_dc.py          # Data center deployment service
│       └── deploy_pop.py         # PoP deployment service
├── tests/                        # Test files
├── .env.example                  # Environment configuration template
├── docker-compose.yml            # Docker composition
├── Dockerfile                    # Container definition
├── pyproject.toml               # Project configuration
├── tasks.py                     # Invoke tasks
└── uv.lock                      # Dependency lock file
```

## Technology Stack

### Core Technologies
- **Python 3.10+**: Primary programming language
- **Streamlit 1.44.1+**: Web application framework
- **Infrahub SDK 1.11.0+**: Infrastructure management integration
- **Polars 1.27.1+**: Data processing (with pandas compatibility)
- **Fast-Depends 2.4.12+**: Dependency injection framework
- **Pydantic 2.5.0+**: Data validation and serialization

### Development Tools
- **UV**: Package and dependency management
- **Ruff**: Code linting and formatting
- **MyPy**: Static type checking
- **Pytest**: Testing framework
- **Invoke**: Task management
- **YAML Lint**: YAML file validation

## Application Architecture

The application follows a modular, service-oriented architecture that provides:

- **Clean Separation**: Each service (connect device, deploy DC, deploy PoP) is self-contained
- **Reusable Components**: Common utilities for validation, help content, and form handling
- **Type Safety**: Comprehensive type hints and validation throughout
- **Maintainability**: Clear code structure with consistent patterns

## Development Setup

### Prerequisites
- Python 3.10 or higher
- UV package manager
- Access to Infrahub instance

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd franc
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set environment variables:**
   ```bash
   export INFRAHUB_ADDRESS="http://your-infrahub-instance"
   ```

4. **Generate schema protocols (if needed):**
   ```bash
   infrahubctl protocols
   ```

5. **Run the application:**
   ```bash
   uv run invoke start
   # or
   uv run streamlit run src/main.py
   ```

### Development Commands

The project uses Invoke for task management:

```bash
# Start the application
uv run invoke start

# Format code
uv run invoke format

# Run linting
uv run invoke lint

# Regenerate Infrahub schema protocols
uv run invoke protocols

# Run tests
uv run pytest

# Type checking
uv run mypy src/
```

## Architecture

### Application Structure

The application follows a modular architecture with clear separation of concerns:

#### Core Components

1. **main.py**: Application entry point with navigation and routing
2. **help_loader.py**: Utility for loading help content from markdown files
3. **infrahub.py**: Infrahub SDK integration and client management
4. **utils.py**: Generic utility functions shared across services
5. **validation.py**: Reusable form validation logic
6. **schema_protocols.py**: Generated Infrahub type definitions

#### Service Modules

Each service is self-contained with:
- Form state management
- Data collection functions
- Validation logic
- UI rendering

### Design Patterns

#### 1. Help Content Management

The application uses external markdown files for all help content:

```python
# Load and display help content
from help_loader import show_help_section, get_cached_help_content

# Display help in an expandable section
show_help_section("Section Title", "help-file-name")

# Load help content for inline use
content = get_cached_help_content("help-file-name")
st.markdown(content)
```

**Help Content Organization:**
- All help files are stored in `src/help/` directory
- Files use `.md` extension and descriptive names
- Content is cached for performance using `@st.cache_data`
- Graceful fallback when files are missing

#### 2. Service Module Pattern

#### 2. Service Module Pattern

Each service follows a consistent structure:

```python
from help_loader import get_cached_help_content, show_help_section

# Form state classes (using NamedTuple)
class ServiceFormState(NamedTuple):
    change_number: str  # Required change management number
    field1: str
    field2: list[Any]
    # ...

# Data collection function
def get_service_form_data() -> dict[str, Any]:
    """Collect form input data for service."""
    # Streamlit form rendering logic with help tooltips
    return form_data

# Validation function
def validate_service_form(state: ServiceFormState) -> list[str]:
    """Validate form fields and return error messages."""
    return collect_validation_errors(...)

# Main form function
def service_form() -> None:
    """Streamlit form for service."""
    # Load help content for instructions
    instructions = get_cached_help_content("service-instructions")
    st.markdown(f"📋 {instructions}")
    
    # Form rendering and submission logic with external help content
```

#### 3. Validation Pattern

Consistent validation across all forms:

```python
def validate_service_form(state: FormState) -> list[str]:
    return collect_validation_errors(
        validate_required_field(state.field1, "Field 1"),
        validate_required_selection(state.options, state.selection, "Selection"),
        custom_validation_function(state.field2),
    )
```

#### 4. Data Loading Pattern

Safe data loading with fallbacks and help integration:

```python
def get_service_form_data() -> dict[str, Any]:
    options = safe_select_options(SchemaType, filters={"key": "value"})
    
    if options:
        field = st.selectbox(
            "Label *", 
            options, 
            key="field_key",
            help="Contextual help text for this field"
        )
    else:
        field = st.text_input(
            "Label * (Manual Entry)", 
            key="field_manual_key",
            help="Manual entry help when external data unavailable",
            placeholder="e.g., example value"
        )
        st.info("💡 Options are not available. Using manual entry mode.")
    
    return {"field": field, "field_options": options}
```

## Code Standards

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Form State Classes**: `{Service}FormState`
- **Data Collection Functions**: `get_{service}_form_data()`
- **Validation Functions**: `validate_{service}_form()`
- **Main Form Functions**: `{service}_form()`

### Type Hints

All functions must include type hints:

```python
def function_name(param: str, optional_param: int = 0) -> ReturnType:
    """Function docstring."""
    pass
```

### Error Handling

- Use `safe_select_options()` for external data loading
- Provide manual input fallbacks when external data unavailable
- Return descriptive error messages from validation functions
- Use `collect_validation_errors()` to aggregate validation results

### Documentation Standards

- All functions require docstrings
- Use descriptive parameter and return type hints
- Document complex business logic with inline comments
- Maintain user and developer documentation
- **Help content is managed in external markdown files**

## Help Content Management

### Help File Organization

Help content is stored in `src/help/` directory as markdown files:

```
src/help/
├── quick-help.md              # General portal help
├── deploy-dc.md               # Data center service overview  
├── deploy-pop.md              # PoP service overview
├── connect-device.md          # Device connection overview
├── interface-config.md        # Interface configuration guide
├── validation-tips.md         # Common validation errors
├── deploy-dc-instructions.md  # DC form instructions
├── deploy-pop-instructions.md # PoP form instructions
├── connect-device-instructions.md # Connection form instructions
├── dc-next-steps.md          # DC success follow-up
├── pop-next-steps.md         # PoP success follow-up
└── connection-next-steps.md  # Connection success follow-up
```

### Adding New Help Content

1. **Create help file**:
   ```bash
   touch src/help/new-help-topic.md
   ```

2. **Add content using standard markdown**:
   ```markdown
   **Section Title:**
   - Bullet point with information
   - Additional guidance
   
   **Tips:**
   - Helpful suggestions
   - Best practices
   ```

3. **Use in application**:
   ```python
   from help_loader import show_help_section, get_cached_help_content
   
   # Display as expandable section
   show_help_section("Title", "new-help-topic")
   
   # Load for inline use
   content = get_cached_help_content("new-help-topic")
   st.markdown(content)
   ```

### Help Content Guidelines

- **Keep content concise** - Users scan rather than read
- **Use consistent formatting** - Follow established patterns
- **Include practical examples** - Show real-world usage
- **Update content regularly** - Keep information current
- **Test all help files** - Ensure they load without errors

### Performance Considerations

- Help content is cached using `@st.cache_data`
- Files are loaded once per session for performance
- Missing files gracefully display error messages
- Large help files are automatically handled

## Testing


### Test Structure

```
tests/
├── __init__.py
├── test_validation.py      # Validation function tests
├── test_utils.py          # Utility function tests (covers all dynamic field/session logic)
├── test_help_loader.py    # Help content loader tests
├── test_simple_structures.py # Data structure tests
├── test_workflow_engine.py   # Workflow engine tests
└── test_services/         # Service-specific tests
    ├── test_connect_device.py
    ├── test_deploy_dc.py
    └── test_deploy_pop.py
```


### Testing Guidelines

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test service workflows end-to-end
3. **Validation Tests**: Comprehensive validation logic testing
4. **Mock External Dependencies**: Mock Infrahub SDK and Streamlit in tests
5. **Path Handling**: Utility tests use `pathlib.Path` for sys.path setup to ensure correct module resolution
6. **Session State**: All dynamic field/session logic in `utils.py` is covered by tests using Streamlit mocks


### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_utils.py

# Run with verbose output
uv run pytest -v
```

## Configuration

### Environment Variables

- `INFRAHUB_ADDRESS`: Infrahub instance URL (required)

### pyproject.toml Configuration

Key configuration sections:

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "D",      # pydocstyle
    "DOC",    # pydoclint
    "CPY",    # flake8-copyright
    "T201",   # use of `print`
    # ... other ignores
]

[tool.mypy]
pretty = true
ignore_missing_imports = true
disallow_untyped_defs = true
```

## Contributing

### Development Workflow

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**:
   - Follow code standards and patterns
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Quality Checks**:
   ```bash
   uv run invoke format    # Format code
   uv run invoke lint      # Check linting
   uv run mypy src/       # Type checking
   uv run pytest         # Run tests
   ```

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Submit Pull Request**:
   - Include description of changes
   - Reference related issues
   - Ensure CI passes

### Adding New Services

To add a new service:

1. **Create Service Module**:
   ```bash
   touch src/services/new_service.py
   ```

2. **Implement Service Pattern**:
   ```python
   # Follow the established service module pattern
   class NewServiceFormState(NamedTuple):
       # Define form state
   
   def get_new_service_form_data() -> dict[str, Any]:
       # Data collection logic
   
   def validate_new_service_form(state: NewServiceFormState) -> list[str]:
       # Validation logic
   
   def new_service_form() -> None:
       # Main form function
   ```

3. **Add to Main Navigation**:
   ```python
   # In src/main.py
   from services.new_service import new_service_form
   
   # Add to service selection
   if service == "New Service":
       new_service_form()
   ```

4. **Add Tests**:
   ```bash
   touch tests/test_services/test_new_service.py
   ```

### Change Management Requirements

All service forms require a change management number:

- **Field Name**: `change_number` (str)
- **Validation**: Required field, cannot be empty
- **Format**: Typically CHG-YYYY-XXXXXX (e.g., CHG-2024-001234)
- **Position**: First field in all forms for immediate visibility
- **Help Text**: Clear explanation of change management requirement

**Implementation Pattern:**
```python
change_number = st.text_input(
    "Change Number *",
    key="service_change_number",
    help="Enter the change management number for this request. Required for tracking and approval.",
    placeholder="e.g., CHG-2024-001234",
)
```

**Validation:**
```python
validate_required_field(state.change_number, "Change Number")
```

### Code Review Checklist

- [ ] Code follows established patterns and naming conventions
- [ ] All functions have type hints and docstrings
- [ ] Tests added for new functionality
- [ ] Linting and type checking pass
- [ ] Error handling includes user-friendly messages
- [ ] Mobile-responsive design considerations
- [ ] Documentation updated if needed

docker run -p 8501:8501 -e INFRAHUB_ADDRESS="http://infrahub" franc

## API Integration

### Infrahub SDK Usage

The application integrates with Infrahub using the official SDK:

```python
from infrahub_sdk import InfrahubClientSync, Config


    address = os.environ.get("INFRAHUB_ADDRESS")
    return InfrahubClientSync(address=address, config=Config(default_branch=branch))
```

### Schema Protocols

Generated protocols provide type-safe access to Infrahub schemas:

```python
from schema_protocols import LocationBuilding, DesignTopology

# Use in safe_select_options
location_options = safe_select_options(LocationBuilding)
design_options = safe_select_options(DesignTopology, filters={"type__value": "DC"})
```

### Error Handling & Test Coverage

External API calls are wrapped with error handling:

```python
def safe_select_options(kind: type, **kwargs: Any) -> list:
    try:
        return select_options(kind, **kwargs)
    except Exception as e:
        st.error(f"Failed to load options: {e}")
        return []
```

#### Utility Function Tests

All dynamic field/session logic in `src/utils.py` is covered by unit tests in `tests/test_utils.py`. Streamlit is fully mocked, and `pathlib.Path` is used for sys.path setup to ensure correct imports.
def get_client(branch: str = "main") -> InfrahubClientSync:
    address = os.environ.get("INFRAHUB_ADDRESS")
    return InfrahubClientSync(address=address, config=Config(default_branch=branch))
```

### Schema Protocols

Generated protocols provide type-safe access to Infrahub schemas:

```python
from schema_protocols import LocationBuilding, DesignTopology

# Use in safe_select_options
location_options = safe_select_options(LocationBuilding)
design_options = safe_select_options(DesignTopology, filters={"type__value": "DC"})
```

### Error Handling

External API calls are wrapped with error handling:

```python
def safe_select_options(kind: type, **kwargs: Any) -> list:
    try:
        return select_options(kind, **kwargs)
    except Exception as e:
        st.error(f"Failed to load options: {e}")
        return []
```

## Troubleshooting

### Common Development Issues

**Import Errors**:
- Ensure virtual environment is activated: `uv shell`
- Regenerate schema protocols: `infrahubctl protocols`

**Linting Failures**:
- Run formatter: `uv run invoke format`
- Check ignored rules in `pyproject.toml`

**Type Checking Issues**:
- Review function signatures and type hints
- Check for missing imports in type checking blocks

**Streamlit Issues**:
- Clear browser cache and cookies
- Restart Streamlit server
- Check console for JavaScript errors

### Performance Optimization

1. **Use Session State Efficiently**: Minimize expensive operations in reruns
2. **Cache External Calls**: Use `@st.cache_data` for expensive API calls
3. **Optimize Form Rendering**: Use containers and columns for layout
4. **Monitor Memory Usage**: Track session state size and cleanup

### Debugging

```python
# Debug mode in Streamlit
if st.checkbox("Debug Mode"):
    st.write("Session State:", st.session_state)
    st.write("Form State:", form_state)
```

## Security Considerations

### Input Validation
- All user inputs are validated before processing
- SQL injection protection through parameterized queries
- XSS prevention through proper Streamlit component usage

### Data Handling
- No sensitive data stored in browser sessions
- Form data validated server-side
- Integration with existing authentication systems

### Infrastructure Security
- Secure communication with Infrahub instance
- Proper network segmentation
- Regular security updates and patches

---

*For questions about this documentation or the codebase, contact the development team.*
