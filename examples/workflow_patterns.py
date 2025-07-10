"""
Examples of workflow patterns for creating objects and using them as references.
"""

from typing import Any, Dict
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrahub import create_and_save, create_branch
from schema_protocols import LocationMetro, DesignTopology, LocationBuilding
from workflow_engine import WorkflowEngine


# Pattern 1: Create wrapper functions that store references in context
def create_metro_location(form_data: dict[str, Any], context: dict[str, Any]) -> Any:
    """Create a metro location and store it in context for later reference."""
    metro = create_and_save(
        LocationMetro,
        {
            "name": form_data["location"],
            "shortname": form_data["location"][:10],
            "description": f"Metro location for {form_data['dc_name']}",
        },
        branch=context.get("branch_name", "main"),
    )
    
    # Store the created object in context for later use
    context["metro_location"] = metro
    context["metro_location_id"] = metro.id
    
    return metro


def create_building_location(form_data: dict[str, Any], context: dict[str, Any]) -> Any:
    """Create a building location that references the metro location."""
    # Get the metro location from context
    metro_location = context.get("metro_location")
    if not metro_location:
        raise ValueError("Metro location must be created first")
    
    building = create_and_save(
        LocationBuilding,
        {
            "name": f"{form_data['dc_name']}-Building",
            "shortname": form_data["dc_name"][:15],
            "description": f"Building for {form_data['dc_name']}",
            "parent": metro_location.id,  # Reference the metro location
        },
        branch=context.get("branch_name", "main"),
    )
    
    # Store the building in context too
    context["building_location"] = building
    context["building_location_id"] = building.id
    
    return building


# Pattern 2: Create a factory function that returns configured workflow steps
def create_dc_deployment_workflow(form_data: dict[str, Any]) -> WorkflowEngine:
    """Create a complete DC deployment workflow with object references."""
    workflow = WorkflowEngine("Data Center Deployment")
    branch_name = f"implement_{form_data.get('change_number', '').lower()}"
    
    # Step 1: Create branch
    workflow.add_step(
        "Creating deployment branch",
        create_branch,
        branch_name,
    )
    
    # Step 2: Create metro location (uses old pattern with context)
    workflow.add_step(
        "Creating metro location",
        create_metro_location,
        form_data,
        # This step needs context, so we'll use the old pattern
    )
    
    # Step 3: Create building location (references metro)
    workflow.add_step(
        "Creating building location",
        create_building_location,
        form_data,
        # This step also needs context to reference the metro
    )
    
    return workflow


# Pattern 3: Create a stateful workflow builder
class DcDeploymentWorkflowBuilder:
    """Builder class for DC deployment workflows with object references."""
    
    def __init__(self, form_data: dict[str, Any]):
        self.form_data = form_data
        self.branch_name = f"implement_{form_data.get('change_number', '').lower()}"
        self.workflow = WorkflowEngine("Data Center Deployment")
        self.references = {}  # Store object references
        
    def add_branch_creation(self):
        """Add branch creation step."""
        self.workflow.add_step(
            "Creating deployment branch",
            create_branch,
            self.branch_name,
        )
        return self
    
    def add_metro_location_creation(self):
        """Add metro location creation step."""
        def create_metro_with_reference():
            metro = create_and_save(
                LocationMetro,
                {
                    "name": self.form_data["location"],
                    "shortname": self.form_data["location"][:10],
                    "description": f"Metro location for {self.form_data['dc_name']}",
                },
                branch=self.branch_name,
            )
            self.references["metro"] = metro
            return metro
            
        self.workflow.add_step(
            "Creating metro location",
            create_metro_with_reference,
        )
        return self
        
    def add_building_location_creation(self):
        """Add building location creation step."""
        def create_building_with_reference():
            if "metro" not in self.references:
                raise ValueError("Metro location must be created first")
                
            building = create_and_save(
                LocationBuilding,
                {
                    "name": f"{self.form_data['dc_name']}-Building",
                    "shortname": self.form_data["dc_name"][:15],
                    "description": f"Building for {self.form_data['dc_name']}",
                    "parent": self.references["metro"].id,
                },
                branch=self.branch_name,
            )
            self.references["building"] = building
            return building
            
        self.workflow.add_step(
            "Creating building location",
            create_building_with_reference,
        )
        return self
        
    def build(self) -> WorkflowEngine:
        """Build and return the configured workflow."""
        return self.workflow


# Pattern 4: Enhanced workflow engine with object registry
class EnhancedWorkflowEngine(WorkflowEngine):
    """Enhanced workflow engine with built-in object registry."""
    
    def __init__(self, workflow_name: str):
        super().__init__(workflow_name)
        self.object_registry = {}
        
    def add_object_creation_step(
        self, 
        name: str, 
        object_type: type, 
        data_factory: callable,
        reference_key: str,
        branch: str = "main"
    ):
        """Add a step that creates an object and stores it in the registry."""
        def create_and_register():
            data = data_factory(self.object_registry)
            obj = create_and_save(object_type, data, branch=branch)
            self.object_registry[reference_key] = obj
            return obj
            
        self.add_step(name, create_and_register)
        return self
        
    def get_object_reference(self, key: str):
        """Get a stored object reference."""
        return self.object_registry.get(key)


# Usage example for Pattern 4
def create_enhanced_dc_workflow(form_data: dict[str, Any]) -> EnhancedWorkflowEngine:
    """Create DC deployment workflow using enhanced engine."""
    workflow = EnhancedWorkflowEngine("Data Center Deployment")
    branch_name = f"implement_{form_data.get('change_number', '').lower()}"
    
    # Add branch creation
    workflow.add_step("Creating deployment branch", create_branch, branch_name)
    
    # Add metro location creation
    workflow.add_object_creation_step(
        "Creating metro location",
        LocationMetro,
        lambda refs: {
            "name": form_data["location"],
            "shortname": form_data["location"][:10],
            "description": f"Metro location for {form_data['dc_name']}",
        },
        "metro",
        branch_name
    )
    
    # Add building location creation (references metro)
    workflow.add_object_creation_step(
        "Creating building location",
        LocationBuilding,
        lambda refs: {
            "name": f"{form_data['dc_name']}-Building",
            "shortname": form_data["dc_name"][:15],
            "description": f"Building for {form_data['dc_name']}",
            "parent": refs["metro"].id,  # Reference previously created metro
        },
        "building",
        branch_name
    )
    
    return workflow
