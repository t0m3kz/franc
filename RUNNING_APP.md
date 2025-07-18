# FRANC Service Portal - Running the Application

## Problem: Relative Import Error

The application uses relative imports within the `src/` package. When running Python files directly (like `python src/main.py`), Python doesn't recognize the package structure, causing `ImportError: attempted relative import with no known parent package`.

## Solution: Use the Entry Point Script

We've created a `run_app.py` entry point that properly handles the import path setup.

## How to Run the Application

### Option 1: Using the Entry Point (Recommended)
```bash
# For development/testing
python run_app.py

# For Streamlit (web interface)
streamlit run run_app.py
```

### Option 2: Run as a Module
```bash
# From the project root directory
python -m src.main

# Note: This approach works for testing imports but won't work with Streamlit
```

### Option 3: Direct Streamlit Command
```bash
# If you need to run with specific Streamlit options
streamlit run run_app.py --server.port 8503 --server.headless true
```

## Current Status

✅ **Application is working correctly**
- All imports are properly resolved
- The application runs successfully with `streamlit run run_app.py`
- MyPy type checking passes (14/14 files)
- All tests pass (41/41 tests)
- **NEW**: Infrahub connection requirements enforced - no manual fallback entries

## Recent Changes

### Infrahub Connection Requirements
- **Removed manual entry fallbacks** for dropdown fields
- When Infrahub is not available, forms now show clear error messages instead of allowing manual data entry
- Form validation prevents submission when required Infrahub data is missing
- Users must have proper Infrahub connectivity to use the application

### Error Handling
- Clear error messages when Infrahub connection fails
- Detailed configuration help provided when connection issues occur
- Form validation includes Infrahub requirement checks

## Files Modified

- **`run_app.py`**: New entry point script that handles import path setup
- **`src/main.py`**: Main application wrapped in a `main()` function
- **All other files**: Use proper relative imports (`.module` syntax)

## Usage

For regular development and deployment, use:
```bash
streamlit run run_app.py
```

The application will be available at `http://localhost:8501` (or another port if specified).
