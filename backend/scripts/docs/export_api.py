"""
OpenAPI Specification Exporter Module for Garrison API.

This module provides the core functionality for generating an OpenAPI specification
from the Garrison FastAPI application. It is designed to be imported and used by
build scripts, such as `scripts/docs/build_docs.py`, and is not intended to be
run as a standalone script.

Key Features:
- Mocks service-level dependencies (e.g., database, model runners) using a
  flexible configuration, allowing for fast and safe spec generation in isolated
  environments like CI/CD.
- Loads the FastAPI application without initializing heavy resources.
- Injects branding information (e.g., logo, contact, tag groups) into the
  final OpenAPI specification.
- Exposes a `generate_spec` function as its main entry point.
"""
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock

from logger import log

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Configuration for mocking modules and their specific objects
# Mocks are used to prevent heavy service initialization, allowing for fast
# and safe spec generation in isolated environments like CI/CD.
#
# To add a new module to mock:
# 1. Add its full import path to the 'modules' list.
#    e.g., 'utils.new_utility'
#
# To mock a specific object within a module (e.g., a function or global variable):
# 1. Add the module's full import path to the 'objects' dictionary as a key.
# 2. Add the object's name and its mock value (e.g., MagicMock()) as a key-value pair.
#    e.g., 'utils.new_utility': {'some_function': MagicMock()}
MOCK_CONFIG = {
    'modules': [
        'app.services.database.connection',
        'app.services.database.factories',
        'logging'
    ],
    'objects': {
        'app.services.database.connection': {
            'DatabaseConnection': MagicMock()
        },
        'app.services.database.factories': {
            'setup_all_repositories': MagicMock()
        },
        'logging': {
            'getLogger': MagicMock(return_value=MagicMock())
        }
    }
}

BRANDING_CONFIG = {
    'logo': {
        'url': './assets/logo.png', # Placeholder
        'altText': 'EmailEssence API',
        'href': 'https://github.com/EmailEssence/EmailEssence.github.io' # Placeholder
    },
    'api_id': 'emailessence-api',
    'tag_groups': [
        {'name': 'Core Features', 'tags': ['Auth', 'User', 'Emails', 'Summaries']},
        {'name': 'Infrastructure', 'tags': ['Root', 'Health']}
    ]
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def apply_mocks():
    """Apply mocks to prevent heavy service initialization."""
    # Mock modules
    for module_name in MOCK_CONFIG['modules']:
        if module_name not in sys.modules:
            sys.modules[module_name] = MagicMock()

    # Mock specific objects
    for module_name, objects in MOCK_CONFIG['objects'].items():
        # Ensure the module is mocked before trying to set attributes on it
        if module_name not in sys.modules:
            sys.modules[module_name] = MagicMock()
            
        for obj_name, mock_value in objects.items():
            setattr(sys.modules[module_name], obj_name, mock_value)

def add_branding(openapi_spec: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """Add custom branding to the OpenAPI spec."""
    log("ADDING BRANDING...", level="DEBUG", verbose=verbose)
    if "info" not in openapi_spec:
        openapi_spec["info"] = {}
    
    openapi_spec["info"]["x-logo"] = BRANDING_CONFIG['logo']
    openapi_spec["info"]["x-api-id"] = BRANDING_CONFIG['api_id']
    openapi_spec["x-tagGroups"] = BRANDING_CONFIG['tag_groups']
    
    return openapi_spec

def generate_spec(verbose: bool = False) -> Optional[Dict[str, Any]]:
    """Load FastAPI app with mocked dependencies and extract OpenAPI spec."""
    
    # The script is in backend/scripts/docs, so we need to add the backend
    # directory to the path to import 'main'.
    backend_root = Path(__file__).resolve().parent.parent.parent
    
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

    try:
        log(f"Applying mocks and loading app from backend/main.py...", verbose=verbose)
        apply_mocks()

        # Import the app instance from main
        from main import app, lifespan

        # To prevent the lifespan from running, we can temporarily disable it
        # during spec generation.
        original_lifespan = app.router.lifespan
        app.router.lifespan = None

        log("Generating OpenAPI specification...", verbose=verbose)
        openapi_spec = app.openapi()
        
        # Restore the original lifespan if needed, though not critical for a script
        app.router.lifespan = original_lifespan
        
        return add_branding(openapi_spec, verbose=verbose)
        
    except ImportError as e:
        log(f"Failed to import the FastAPI app. Ensure the backend structure is correct. Error: {e}", level="ERROR")
        return None
    finally:
        if str(backend_root) in sys.path:
            sys.path.remove(str(backend_root))

def handle_error(error, context="spec generation"):
    """Log a formatted error message and return an exit code."""
    error_type = type(error).__name__
    log(f"Failed to complete {context} due to {error_type}.", level="ERROR")
    log(f"DETAILS: {error}", level="ERROR")
    return 1


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    log(
        "This script is not meant to be run directly. "
        "Please use the 'scripts/docs/build_docs.py' script to generate documentation.",
        level="ERROR"
    )
    sys.exit(1)
