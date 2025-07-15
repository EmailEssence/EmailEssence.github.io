#!/usr/bin/env python3
"""
Branded Documentation Builder for EmailEssence API

Generates branded API documentation using Redocly CLI. Handles OpenAPI spec generation,
validation, HTML documentation building, asset management, and development server.

Requirements: npm install -g @redocly/cli

Usage:
    poetry run python scripts/docs/build_docs.py -v -r -c
    poetry run python scripts/docs/build_docs.py [--clean] [--report] [--verbose]
    poetry run python scripts/docs/build_docs.py --dev [--verbose]
    poetry run python scripts/docs/build_docs.py --validate
    poetry run python scripts/docs/build_docs.py --install

Options:
    --dev           Start a local development server with live reload.
    --install       Install the Redocly CLI dependency and exit.
    --validate      Validate the configuration and spec, then exit.
    --clean, -c      Clean existing output files before building.
    --report, -r     Generate a validation report in Markdown format.
    --verbose, -v    Enable verbose logging for detailed output.
"""



import argparse
import json
import subprocess
import shutil
import sys
import os
import yaml
from pathlib import Path
from typing import Optional, List

# Insert scripts/docs into the path for local imports
# This allows us to import other scripts in this directory
_scripts_docs_path = Path(__file__).parent.resolve()
sys.path.insert(0, str(_scripts_docs_path))

from logger import log
from export_api import generate_spec, MOCK_CONFIG, BRANDING_CONFIG
from spec_validator import SpecValidator


INSTALL_COMMANDS = [
    (["npm", "install", "-g", "@redocly/cli"], "npm"),
    (["yarn", "global", "add", "@redocly/cli"], "yarn"),
    (["pnpm", "add", "-g", "@redocly/cli"], "pnpm")
]

class DocBuilder:
    """Simplified documentation builder using Redocly CLI."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.redocly_cmd: Optional[str] = None
        self.root_dir = Path.cwd()
        
        self.docs_dir = self.root_dir / "docs" / "api"
        self.config_file = self.docs_dir / "redocly.yaml"
        self.openapi_file = self.docs_dir / "emailessence-openapi.yaml"
        self.assets_dir = self.docs_dir / "assets"
        
    def find_and_validate_redocly(self) -> bool:
        """Find Redocly CLI and validate it works."""
        potential_paths = ["redocly"]

        # Add common Windows paths for nvm and npm for robustness
        if os.name == 'nt':
            nvm_symlink = os.getenv("NVM_SYMLINK")
            if nvm_symlink and Path(nvm_symlink).exists():
                log(f"Found NVM_SYMLINK: {nvm_symlink}", "DEBUG", verbose=self.verbose)
                potential_paths.append(Path(nvm_symlink) / "redocly.cmd")
            
            potential_paths.append(Path.home() / "AppData/Roaming/npm/redocly.cmd")

        # Test each path
        for redocly_path in potential_paths:
            # Resolve the command path using shutil.which
            resolved_path = shutil.which(str(redocly_path))
            if resolved_path:
                try:
                    # On Windows, .cmd files may require shell=True to be found/executed correctly
                    use_shell = os.name == 'nt'
                    # Pass command as a string if using shell=True, quoting the path
                    cmd = f'"{resolved_path}" --version' if use_shell else [resolved_path, "--version"]

                    result = subprocess.run(
                        cmd,
                        shell=use_shell,
                        check=True, capture_output=True, text=True, 
                        encoding='utf-8', errors='replace'
                    )
                    
                    log(f"Found Redocly CLI version {result.stdout.strip()} at {resolved_path}", "SUCCESS", verbose=self.verbose)
                    self.redocly_cmd = resolved_path
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    log(f"Path '{resolved_path}' found but failed to execute.", "DEBUG", verbose=self.verbose)
                    continue
        
        return False
    
    def install_redocly(self) -> bool:
        """Install Redocly CLI using available package manager."""
        log("Installing Redocly CLI globally...", verbose=self.verbose)
        
        for cmd, manager in INSTALL_COMMANDS:
            try:
                log(f"Attempting installation with {manager}...", level="DEBUG", verbose=self.verbose)
                result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
                log(f"Redocly CLI installed successfully using {manager}", "SUCCESS", verbose=self.verbose)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                log(f"Installation with {manager} failed", "WARNING", verbose=self.verbose)
                if self.verbose and hasattr(e, 'stderr') and e.stderr:
                    log(f"Error: {e.stderr}", "DEBUG", verbose=self.verbose)
                continue
        
        log("Could not install Redocly CLI automatically", "ERROR", verbose=self.verbose)
        log("Please install manually: npm install -g @redocly/cli", verbose=self.verbose)
        return False
    
    def validate_config(self) -> bool:
        """Validate Redocly configuration file, creating a default if it doesn't exist."""
        if not self.config_file.exists():
            log(f"Configuration file not found, creating default: {self.config_file}", "WARNING", verbose=self.verbose)
            try:
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
                default_config = {
                    'apis': {
                        'emailessence-api@v1': {
                            'root': f'./{self.openapi_file.name}'
                        }
                    },
                    'theme': {
                        'openapi': {
                            'theme': {
                                'colors': {
                                    'primary': {'main': '#32329f'}
                                }
                            }
                        }
                    }
                }
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(default_config, f, sort_keys=False, default_flow_style=False)
                log("Default configuration file created successfully.", "SUCCESS", verbose=self.verbose)
            except Exception as e:
                log(f"Failed to create default configuration file: {e}", "ERROR", verbose=self.verbose)
                return False

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if not isinstance(config_data, dict) or 'apis' not in config_data:
                log("Configuration file must contain a valid 'apis' section", "ERROR", verbose=self.verbose)
                return False
                
            log("Configuration file validation successful", "SUCCESS", verbose=self.verbose)
            return True
            
        except Exception as e:
            log(f"Configuration validation warning: {e}", "WARNING", verbose=self.verbose)
            return True  # Don't fail build for validation issues
    
    def run_command(self, cmd: List[str], description: str, capture_output: bool = True) -> bool:
        """Run command with error handling."""
        log(f"{description}...", verbose=self.verbose)
        log(f"Executing: {' '.join(cmd)}", "DEBUG", verbose=self.verbose)
        
        try:
            # On Windows, .cmd files may require shell=True
            use_shell = os.name == 'nt'
            cmd_to_run = ' '.join(cmd) if use_shell else cmd

            result = subprocess.run(
                cmd_to_run, 
                shell=use_shell,
                check=True, capture_output=capture_output, text=True, encoding='utf-8', errors='replace'
            )
            if capture_output and result.stdout and self.verbose:
                log(f"Output: {result.stdout}", "DEBUG", verbose=self.verbose)
            return True
            
        except subprocess.CalledProcessError as e:
            log(f"{description} failed!", "ERROR", verbose=self.verbose)
            if e.stdout:
                log(f"STDOUT: {e.stdout}", "ERROR", verbose=self.verbose)
            if e.stderr:
                log(f"STDERR: {e.stderr}", "ERROR", verbose=self.verbose)
            return False
            
        except FileNotFoundError:
            log(f"Command not found: {cmd[0]}", "ERROR", verbose=self.verbose)
            if cmd[0] == self.redocly_cmd:
                log("Run with --install flag to install Redocly CLI", "ERROR", verbose=self.verbose)
            return False
    
    def setup_assets_and_clean(self, clean: bool = False) -> bool:
        """Setup assets and optionally clean output files."""
        if clean:
            log("Cleaning existing output files...", verbose=self.verbose)
            files_to_clean = [
                self.openapi_file,
                self.docs_dir / "index.html",
                self.docs_dir / "validation-report.md"
            ]
            
            cleaned_count = 0
            for file_path in files_to_clean:
                if file_path.exists():
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except OSError as e:
                        log(f"Failed to remove {file_path}: {e}", "WARNING", verbose=self.verbose)
            
            if cleaned_count > 0:
                log(f"Cleaned {cleaned_count} file(s)", "SUCCESS", verbose=self.verbose)
        
        # Setup assets
        log("Setting up documentation assets...", verbose=self.verbose)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        # NOTE: Asset copying is currently disabled as the source is unclear.
        # To enable, update the `source_assets` path and the list of files to copy.
        # source_assets = self.root_dir / "path" / "to" / "assets"
        # assets_to_copy = ["logo.png"]
        
        return True
    
    def generate_spec_and_build_docs(self, dev_mode: bool = False, report: bool = False) -> bool:
        """Generate OpenAPI spec, validate it, and build documentation."""
        log("Generating EmailEssence OpenAPI specification...", verbose=self.verbose)
        openapi_spec = generate_spec(verbose=self.verbose)

        if not openapi_spec:
            log("Failed to generate OpenAPI specification.", "ERROR", verbose=self.verbose)
            return False

        # Validate spec
        doc_tags = {tag for group in BRANDING_CONFIG.get("tag_groups", []) for tag in group.get("tags", [])}
        validator = SpecValidator(openapi_spec, MOCK_CONFIG, doc_tags=doc_tags, verbose=self.verbose)
        is_valid = validator.run_all_checks()

        if report:
            report_content = validator.generate_markdown_report()
            if report_content:
                report_file = self.docs_dir / "validation-report.md"
                try:
                    report_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(report_file, "w", encoding="utf-8") as f:
                        f.write(report_content)
                    log(f"Validation report written to {report_file}", "SUCCESS", verbose=self.verbose)
                except IOError as e:
                    log(f"Failed to write validation report: {e}", "ERROR", verbose=self.verbose)
            else:
                log("No validation issues found, report not generated.", verbose=self.verbose)

        if not is_valid:
            log("Specification is invalid, aborting build.", "ERROR", verbose=self.verbose)
            return False

        # Write spec to file
        try:
            self.openapi_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.openapi_file, "w", encoding="utf-8") as f:
                yaml.dump(openapi_spec, f, sort_keys=False, default_flow_style=False)
            log(f"Specification written to {self.openapi_file}", "SUCCESS", verbose=self.verbose)
        except IOError as e:
            log(f"Failed to write OpenAPI spec: {e}", "ERROR", verbose=self.verbose)
            return False
        
        # Build documentation
        if dev_mode:
            log("Starting development server with live reload...", verbose=self.verbose)
            log("Development server will be available at http://localhost:8080", verbose=self.verbose)
            log("Press Ctrl+C to stop the server", verbose=self.verbose)
            
            return self.run_command([
                self.redocly_cmd, "preview-docs", "emailessence-api@v1", 
                "--port", "8080",
                "--config", str(self.config_file)
            ], "Starting development server", capture_output=False)
        else:
            output_file = self.docs_dir / "index.html"
            return self.run_command([
                self.redocly_cmd, "build-docs", "emailessence-api@v1", 
                "--output", str(output_file),
                "--config", str(self.config_file)
            ], "Building static HTML documentation")
    
    def build(self, dev_mode: bool = False, clean: bool = False, validate_only: bool = False, install: bool = False, report: bool = False) -> bool:
        """Complete build process for API documentation."""
        log("🚀 Building EmailEssence API Documentation", verbose=self.verbose)
        log("=" * 70, verbose=self.verbose)
        
        if install:
            return self.install_redocly()
        
        if not self.find_and_validate_redocly():
            log("Redocly CLI is not installed or not in PATH", "ERROR", verbose=self.verbose)
            log("Run with --install flag to install automatically", "ERROR", verbose=self.verbose)
            return False
        
        if not self.validate_config():
            log("Configuration validation failed", "ERROR", verbose=self.verbose)
            return False
        
        if validate_only:
            log("Configuration validation completed successfully", "SUCCESS", verbose=self.verbose)
            return True
        
        if not self.setup_assets_and_clean(clean):
            return False
        
        if not self.generate_spec_and_build_docs(dev_mode, report=report):
            return False
        
        if not dev_mode:
            log("\n🎉 Documentation built successfully!", "SUCCESS", verbose=self.verbose)
            log("📁 Output files:", verbose=self.verbose)
            log(f"  - {self.openapi_file} (OpenAPI specification)", verbose=self.verbose)
            log(f"  - {self.docs_dir / 'index.html'} (Branded HTML documentation)", verbose=self.verbose)
            log(f"  - {self.assets_dir } (Logo and branding assets)", verbose=self.verbose)
            if report and (self.docs_dir / "validation-report.md").exists():
                log(f"  - {self.docs_dir / 'validation-report.md'} (Validation Report)", verbose=self.verbose)
        
        return True

def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Advanced API documentation builder for EmailEssence using Redocly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
        # Suggested usage (clean, verbose, report)
        python scripts/docs/build_docs.py -c -v -r

        # Build static documentation
        python scripts/docs/build_docs.py

        # Start development server with verbose logging
        python scripts/docs/build_docs.py --dev --verbose

        # Clean and build, generating a validation report
        python scripts/docs/build_docs.py --clean --report
        """
    )
    
    parser.add_argument("--dev", action="store_true", help="Start development server with live reload")
    parser.add_argument("--install", action="store_true", help="Install Redocly CLI globally and exit")
    parser.add_argument("--validate", action="store_true", help="Validate Redocly configuration and exit")
    parser.add_argument("--clean", "-c", action="store_true", help="Clean existing output files before building")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--report", "-r", action="store_true", help="Generate a validation report in Markdown format")
    
    args = parser.parse_args()
    
    builder = DocBuilder(verbose=args.verbose)
    
    if args.install:
        success = builder.install_redocly()
        if success:
            log("✅ Redocly CLI installation completed!", "SUCCESS", verbose=True)
            log("You can now run: python scripts/build-docs.py", verbose=True)
        sys.exit(0 if success else 1)
    
    success = builder.build(
        dev_mode=args.dev,
        clean=args.clean,
        validate_only=args.validate,
        report=args.report
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 