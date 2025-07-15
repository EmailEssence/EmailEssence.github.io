"""
API Specification Validator for Garrison.

This module provides the SpecValidator class, which is responsible for running
a series of checks on the generated OpenAPI specification to ensure its
correctness, completeness, and adherence to project standards.
"""
from typing import Any, Dict, List, Optional

from logger import log


class SpecValidator:
    """A class to validate the OpenAPI specification for correctness and completeness."""

    def __init__(self, openapi_spec: Dict[str, Any], mock_config: Dict[str, Any], doc_tags: set = None, verbose: bool = False):
        """
        Initialize the validator.

        Args:
            openapi_spec (Dict[str, Any]): The OpenAPI specification dictionary.
            mock_config (Dict[str, Any]): The mock configuration.
            doc_tags (set, optional): A set of tags for documentation purposes.
            verbose (bool, optional): Enable verbose logging. Defaults to False.
        """
        self.spec = openapi_spec
        self.mock_config = mock_config
        self.doc_tags = doc_tags if doc_tags is not None else set()
        self.paths = openapi_spec.get("paths", {})
        self.issues: List[Dict[str, Any]] = []
        self.verbose = verbose
        self._validated_schemas = set()

    def run_all_checks(self) -> bool:
        """Run all validation checks and return True if no critical issues were found."""
        log("RUNNING API SPECIFICATION VALIDATIONS...", verbose=self.verbose)
        
        endpoints_data = self.collect_endpoints_data()

        self.display_tag_analysis(endpoints_data)
        self._check_untagged_endpoints(endpoints_data["untagged"])
        self._check_missing_summary()
        self._check_missing_property_descriptions()
        self._check_missing_type_hints()
        
        errors = [i for i in self.issues if i.get('level') == 'error']
        warnings = [i for i in self.issues if i.get('level') == 'warning']

        if warnings:
            log(f"VALIDATION FOUND {len(warnings)} WARNING(S):", level="WARNING", verbose=self.verbose)
            for issue in warnings:
                log(self._format_issue_for_console(issue), level="WARNING", verbose=self.verbose)

        if errors:
            log(f"VALIDATION FAILED: Found {len(errors)} CRITICAL issue(s).", level="ERROR", verbose=self.verbose)
            for issue in errors:
                log(self._format_issue_for_console(issue), level="ERROR", verbose=self.verbose)
            return False
        
        log("All validation checks passed!", level="SUCCESS", verbose=self.verbose)
        return True

    # ==============================================================================
    # FORMATTING AND REPORTING
    # ==============================================================================

    def _format_issue_for_console(self, issue: Dict[str, Any]) -> str:
        """Format a structured issue for readable console logging."""
        title = issue['title']
        details = issue.get('details', [])
        footer = issue.get('footer', '')
        level = issue.get('level', 'warning').upper()

        message = f"[{level}] {title}"
        if details:
            sorted_details = sorted(details, key=self._get_route_sort_key) if issue.get("sort_by_route") else sorted(details)
            details_str = "\n".join(f"    - {item}" for item in sorted_details)
            message += f":\n{details_str}"
        
        if footer:
            message += f"\n\nNote: {footer}"
            
        return message

    def _get_route_sort_key(self, endpoint_string: str) -> tuple:
        """Create a sort key for an endpoint string to sort by path, then method."""
        parts = endpoint_string.split()
        if len(parts) >= 2 and parts[0].isalpha() and parts[1].startswith('/'):
            method = parts[0]
            path = parts[1]
            return (path, method)
        # Fallback for other detail strings
        return (endpoint_string,)

    def generate_markdown_report(self) -> Optional[str]:
        """Generate a markdown report of all validation issues."""
        if not self.issues:
            return None

        report_parts = ["# API Specification Validation Report\n\n"]
        total_issues = sum(len(i.get('details', [])) for i in self.issues)
        report_parts.append(f"Found **{total_issues}** total issue(s) across **{len(self.issues)}** categories.\n")
        
        # Separate errors and warnings
        errors = [i for i in self.issues if i.get('level') == 'error']
        warnings = [i for i in self.issues if i.get('level') == 'warning']

        if errors:
            report_parts.append("## 🚨 Critical Errors\n")
            for issue in errors:
                report_parts.append(self._format_issue_for_markdown(issue))

        if warnings:
            report_parts.append("## ⚠️ Warnings\n")
            for issue in warnings:
                report_parts.append(self._format_issue_for_markdown(issue))
            
        return "\n".join(report_parts)

    def _format_issue_for_markdown(self, issue: Dict[str, Any]) -> str:
        """Helper to format a single issue for the markdown report."""
        title = issue['title']
        details = issue.get('details', [])
        footer = issue.get('footer', '')
        
        part = f"### {title}\n"

        sorted_details = sorted(details, key=self._get_route_sort_key) if issue.get("sort_by_route") else sorted(details)

        if sorted_details:
            for item in sorted_details:
                part += f"- `{item}`\n"
        if footer:
            part += f"\n> **Note:** {footer}\n"
        part += "\n---\n"
        return part

    # ==============================================================================
    # DATA COLLECTION AND ANALYSIS
    # ==============================================================================

    def display_tag_analysis(self, endpoints_data: Dict[str, Any]):
        """Display a breakdown of endpoint groupings by tag in verbose mode."""
        log("ANALYZING TAGS...", level="DEBUG", verbose=self.verbose)
    
        endpoints_by_tag = endpoints_data['by_tag']
        untagged_count = len(endpoints_data['untagged'])
        total_endpoints = sum(len(e) for e in endpoints_by_tag.values()) + untagged_count
        tagged_endpoints = total_endpoints - untagged_count

        log(f"Found {len(endpoints_by_tag)} tag groups covering {tagged_endpoints}/{total_endpoints} endpoints.", verbose=self.verbose)
    
        if endpoints_by_tag:
            log("\nEndpoint grouping by tags:", level="DEBUG", verbose=self.verbose)
            for tag, endpoints in sorted(endpoints_by_tag.items()):
                log(f"  {tag} ({len(endpoints)} endpoints)", level="DEBUG", verbose=self.verbose)
                for endpoint in sorted(endpoints):
                    log(f"    - {endpoint}", level="DEBUG", verbose=self.verbose)

        if untagged_count == 0:
            log("All endpoints are properly tagged!", level="SUCCESS", verbose=self.verbose)

    def collect_endpoints_data(self) -> Dict[str, Any]:
        """Collect and return a summary of endpoint data."""
        all_tags = set()
        untagged_endpoints = []
        endpoints_by_tag = {}

        for path, methods in self.paths.items():
            for method, details in methods.items():
                endpoint = f"{method.upper()} {path}"
                tags = details.get("tags", [])

                if not tags:
                    untagged_endpoints.append(endpoint)
                else:
                    all_tags.update(tags)
                    for tag in tags:
                        endpoints_by_tag.setdefault(tag, []).append(endpoint)
        
        return {
            "all_tags": all_tags,
            "untagged": untagged_endpoints,
            "by_tag": endpoints_by_tag,
        }

    # ==============================================================================
    # VALIDATION CHECKS
    # ==============================================================================

    def _check_untagged_endpoints(self, untagged_endpoints: list):
        """Check for endpoints that are not assigned to any tag group."""
        if untagged_endpoints:
            # Filter out the root path, which is often untagged by design
            filtered_untagged = [ep for ep in untagged_endpoints if not ep.endswith(" /")]
            if filtered_untagged:
                self.issues.append({
                    "level": "warning",
                    "title": f"Found {len(filtered_untagged)} untagged endpoints",
                    "details": filtered_untagged,
                    "sort_by_route": True,
                    "footer": "Add a `tags=['YourTag']` to each of your path operations in the router."
                })

    def _check_missing_summary(self):
        """Check for missing summary (line 1 of docstring) in endpoints."""
        missing = []
        for path, methods in self.paths.items():
            for method, details in methods.items():
                # The root path and health checks are special cases that don't need a summary
                if path in ["/", "/health"]:
                    continue
                if not details.get("summary", "").strip():
                    endpoint = f"{method.upper()} {path}"
                    missing.append(endpoint)
        
        if missing:
            self.issues.append({
                "level": "error",
                "title": f"Found {len(missing)} endpoints missing a summary",
                "details": missing,
                "footer": "The summary is the first line of the endpoint's docstring and is required.",
                "sort_by_route": True,
            })
            
    def _check_missing_docstrings(self):
        """Checks for endpoints that are likely missing docstrings by checking for auto-generated summaries."""
        missing = []
        for path, methods in self.paths.items():
            for method, details in methods.items():
                summary = details.get("summary", "").strip()
                operation_id = details.get("operationId", "")
                description = details.get("description", "").strip()

                if not summary or not operation_id:
                    continue

                # If a description exists, a multi-line docstring is present.
                if description:
                    continue

                # Heuristic to detect auto-generation from function name.
                # e.g., summary "My Endpoint Name" -> "my_endpoint_name"
                # We check if the operationId starts with this.
                reconstructed_func_name = summary.replace(' ', '_').lower()
                if operation_id.startswith(reconstructed_func_name):
                    endpoint = f"{method.upper()} {path}"
                    handler_func = operation_id.split('_')[0]
                    missing.append(f"{endpoint} (handler: `{handler_func}`)")
        
        if missing:
            self.issues.append({
                "level": "warning",
                "title": f"Found {len(missing)} endpoints with auto-generated summaries",
                "details": missing,
                "footer": "These summaries were auto-generated from the handler function name. Add a docstring to each handler to provide a meaningful summary and description.",
                "sort_by_route": True,
            })



    def _check_missing_property_descriptions(self):
        """Check for properties in Pydantic models that are missing a description."""
        missing_by_schema = {}
        schemas = self.spec.get("components", {}).get("schemas", {})

        for schema_name, schema_def in schemas.items():
            if schema_def.get("type") == "object" and "properties" in schema_def:
                if schema_name.startswith("Body_") or schema_name in ["ValidationError", "HTTPValidationError"]:
                    continue
                
                missing_props = []
                for prop_name, prop_schema in schema_def["properties"].items():
                    if not prop_schema.get("description", "").strip():
                        missing_props.append(f"'{prop_name}'")
                
                if missing_props:
                    has_model_description = bool(schema_def.get("description", "").strip())
                    missing_by_schema[schema_name] = {
                        "properties": missing_props,
                        "has_model_description": has_model_description
                    }

        if not missing_by_schema:
            return
            
        details = []
        total_missing_count = 0
        for schema_name, data in sorted(missing_by_schema.items()):
            total_missing_count += len(data["properties"])
            props_list_str = ", ".join(sorted(data["properties"]))
            
            verbiage = "may be missing descriptions for" if data["has_model_description"] else "is missing descriptions for"
            details.append(f"Schema '{schema_name}' {verbiage} properties: {props_list_str}")

        if details:
            self.issues.append({
                "level": "warning",
                "title": f"Found {total_missing_count} model properties missing a description",
                "details": details,
                "footer": "Add a `description` to your Pydantic `Field` to provide a clear explanation for each property."
            })

    def _recursive_check_schema(self, schema: Dict[str, Any], context: str):
        """Recursively check a schema for untyped properties (e.g., 'Any')."""
        if not isinstance(schema, dict):
            return

        # If it's a reference, resolve it and check the component schema.
        if "$ref" in schema:
            ref_path = schema["$ref"].split('/')
            if len(ref_path) == 4 and ref_path[0] == '#' and ref_path[1] == 'components' and ref_path[2] == 'schemas':
                schema_name = ref_path[3]
                
                if schema_name in self._validated_schemas:
                    return
                self._validated_schemas.add(schema_name)
                
                component_schemas = self.spec.get("components", {}).get("schemas", {})
                if schema_name in component_schemas:
                    self._recursive_check_schema(component_schemas[schema_name], f"schema '{schema_name}'")
            return

        # An untyped schema (no type, ref, etc.) is likely an 'Any' type.
        has_type_info = any(key in schema for key in ["type", "$ref", "anyOf", "oneOf", "allOf", "not"])
        if not has_type_info:
            title = "Ambiguous type (likely 'Any') used in schema"
            detail_str = f"In {context}"

            existing_issue = next((issue for issue in self.issues if issue['title'] == title), None)

            if existing_issue:
                if detail_str not in existing_issue['details']:
                    existing_issue['details'].append(detail_str)
            else:
                self.issues.append({
                    "level": "warning",
                    "title": title,
                    "details": [detail_str],
                    "footer": "Explicitly type properties in your Pydantic models instead of using 'Any'."
                })
            return

        # Recurse into object properties.
        if schema.get("type") == "object" and "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                self._recursive_check_schema(prop_schema, f"property '{prop_name}' in {context}")

        # Recurse into array items.
        if schema.get("type") == "array" and "items" in schema:
            self._recursive_check_schema(schema["items"], f"items in {context}")

    def _check_missing_type_hints(self):
        """Check all schemas for ambiguous properties that likely come from 'Any' type hints."""
        # Reset the validated schemas for each run
        self._validated_schemas = set()

        # Check schemas used in endpoints
        for path, methods in self.paths.items():
            for method, details in methods.items():
                endpoint = f"{method.upper()} {path}"
                
                for param in details.get("parameters", []):
                    if "schema" in param:
                        self._recursive_check_schema(param["schema"], f"parameter '{param['name']}' in {endpoint}")
                
                request_body = details.get("requestBody", {})
                if request_body and "content" in request_body:
                    for media_type, content in request_body["content"].items():
                        if "schema" in content:
                            self._recursive_check_schema(content["schema"], f"request body ({media_type}) in {endpoint}")

                for code, response in details.get("responses", {}).items():
                    if "content" in response:
                        for media_type, content in response["content"].items():
                            if "schema" in content:
                                self._recursive_check_schema(content["schema"], f"response {code} ({media_type}) in {endpoint}")
        
        # Check all component schemas to catch unused ones
        all_schemas = self.spec.get("components", {}).get("schemas", {})
        for schema_name, schema_def in all_schemas.items():
            if schema_name not in self._validated_schemas:
                self._recursive_check_schema(schema_def, f"schema '{schema_name}'") 