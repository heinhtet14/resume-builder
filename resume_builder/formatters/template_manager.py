# Modified resume_builder/formatters/template_manager.py with debug output

import os
from pathlib import Path
from typing import List, Dict, Optional

class TemplateManager:
    """Manage and select resume templates."""
    
    def __init__(self, template_dir=None):
        if template_dir is None:
            # Use the templates directory relative to the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            template_dir = os.path.join(base_dir, "templates")
        
        self.template_dir = Path(template_dir)
        self._templates = None
        
        # Debug output
        print(f"Template directory: {self.template_dir}")
        print(f"Template directory exists: {self.template_dir.exists()}")
    
    @property
    def templates(self) -> Dict[str, str]:
        """Get available templates with names as keys and filenames as values."""
        if self._templates is None:
            self._templates = self._scan_templates()
        return self._templates
    
    def _scan_templates(self) -> Dict[str, str]:
        """Scan the template directory for HTML templates."""
        templates = {}
        
        if not self.template_dir.exists():
            print(f"Warning: Template directory not found: {self.template_dir}")
            return templates
        
        # Look for HTML files in the template directory
        print(f"Scanning for templates in: {self.template_dir}")
        for file_path in self.template_dir.glob("*.html"):
            # Use filename without extension as template name
            template_name = file_path.stem
            
            # Format the name to be more readable (replace underscores with spaces, capitalize)
            display_name = template_name.replace("_", " ").title()
            
            templates[display_name] = file_path.name
            print(f"Found template: {display_name} ({file_path.name})")
        
        if not templates:
            print(f"Warning: No templates found in {self.template_dir}")
            
        return templates
    
    def get_template_list(self) -> List[str]:
        """Get a list of available template names."""
        template_list = list(self.templates.keys())
        print(f"Available templates: {template_list}")
        return template_list
    
    def get_template_filename(self, template_name: str) -> Optional[str]:
        """Get the filename for a template by its name."""
        filename = self.templates.get(template_name)
        print(f"Getting template filename for '{template_name}': {filename}")
        return filename