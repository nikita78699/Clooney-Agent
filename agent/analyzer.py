from typing import Dict, List
import json

class APIAnalyzer:
    def __init__(self, api_spec: Dict):
        self.api_spec = api_spec
        
    def analyze_schema(self) -> Dict:
        """Analyze API schema and generate database schema"""
        schemas = self.api_spec.get("schemas", {})
        db_schema = {}
        
        for model_name, fields in schemas.items():
            table_name = model_name.lower() + "s"
            db_schema[table_name] = {
                "columns": self._convert_fields_to_columns(fields),
                "relationships": self._extract_relationships(fields)
            }
        
        return db_schema
    
    def _convert_fields_to_columns(self, fields: Dict) -> List[Dict]:
        """Convert API fields to database columns"""
        type_mapping = {
            "string": "VARCHAR(255)",
            "text": "TEXT",
            "boolean": "BOOLEAN",
            "date": "DATE",
            "datetime": "TIMESTAMP",
            "integer": "INTEGER"
        }
        
        columns = [
            {"name": "id", "type": "SERIAL PRIMARY KEY", "nullable": False}
        ]
        
        for field_name, field_type in fields.items():
            if field_name == "gid":
                columns.append({
                    "name": "gid",
                    "type": "VARCHAR(255) UNIQUE",
                    "nullable": False
                })
            elif field_name in ["workspace", "project", "assignee", "parent", "task", "created_by"]:
                # These are foreign keys
                columns.append({
                    "name": field_name + "_id",
                    "type": "INTEGER",
                    "nullable": True,
                    "foreign_key": field_name + "s"
                })
            elif field_name == "notes":
                columns.append({
                    "name": field_name,
                    "type": "TEXT",
                    "nullable": True
                })
            else:
                columns.append({
                    "name": field_name,
                    "type": type_mapping.get(field_type, "VARCHAR(255)"),
                    "nullable": True
                })
        
        # Add standard timestamps
        columns.extend([
            {"name": "created_at", "type": "TIMESTAMP", "nullable": False, "default": "CURRENT_TIMESTAMP"},
            {"name": "updated_at", "type": "TIMESTAMP", "nullable": False, "default": "CURRENT_TIMESTAMP"}
        ])
        
        return columns
    
    def _extract_relationships(self, fields: Dict) -> List[Dict]:
        """Extract relationships between models"""
        relationships = []
        
        for field_name, field_type in fields.items():
            if field_name in ["workspace", "project", "assignee", "parent", "task", "created_by"]:
                relationships.append({
                    "field": field_name + "_id",
                    "references": field_name + "s"
                })
        
        return relationships
    
    def generate_openapi_spec(self) -> Dict:
        """Generate OpenAPI specification"""
        openapi = {
            "openapi": "3.0.0",
            "info": {
                "title": "Asana Clone API",
                "version": "1.0.0",
                "description": "Clone of Asana API for Tasks, Projects, and Sections"
            },
            "paths": {},
            "components": {
                "schemas": {}
            }
        }
        
        # Generate schemas
        for model_name, fields in self.api_spec.get("schemas", {}).items():
            openapi["components"]["schemas"][model_name] = {
                "type": "object",
                "properties": self._convert_to_openapi_properties(fields)
            }
        
        # Generate paths
        for endpoint in self.api_spec.get("endpoints", []):
            path = endpoint["path"]
            method = endpoint["method"].lower()
            
            if path not in openapi["paths"]:
                openapi["paths"][path] = {}
            
            openapi["paths"][path][method] = self._generate_endpoint_spec(endpoint)
        
        return openapi
    
    def _convert_to_openapi_properties(self, fields: Dict) -> Dict:
        """Convert fields to OpenAPI properties"""
        type_mapping = {
            "string": "string",
            "text": "string",
            "boolean": "boolean",
            "date": "string",
            "datetime": "string",
            "integer": "integer"
        }
        
        properties = {}
        for field_name, field_type in fields.items():
            properties[field_name] = {
                "type": type_mapping.get(field_type, "string")
            }
            if field_type == "date":
                properties[field_name]["format"] = "date"
        
        return properties
    
    def _generate_endpoint_spec(self, endpoint: Dict) -> Dict:
        """Generate OpenAPI spec for an endpoint"""
        resource = endpoint["resource"].rstrip('s').capitalize()
        
        spec = {
            "summary": endpoint["name"].replace("_", " ").title(),
            "operationId": endpoint["name"],
            "tags": [endpoint["resource"]]
        }
        
        # Parameters
        if "{" in endpoint["path"]:
            spec["parameters"] = []
            import re
            params = re.findall(r'\{(\w+)\}', endpoint["path"])
            for param in params:
                spec["parameters"].append({
                    "name": param,
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                })
        
        # Request body for POST/PUT
        if endpoint["method"] in ["POST", "PUT"]:
            spec["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{resource}"}
                    }
                }
            }
        
        # Responses
        spec["responses"] = {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{resource}"}
                    }
                }
            }
        }
        
        return spec
