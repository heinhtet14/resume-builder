import os
from jinja2 import Environment, FileSystemLoader
from resume_builder.models.resume import Resume

class HtmlFormatter:
    """Format a resume as HTML using a template."""
    
    def __init__(self, template_dir=None, template_name="harvard.html"):
        if template_dir is None:
            # Use the templates directory relative to the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            template_dir = os.path.join(base_dir, "templates")
        
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template_name = template_name
    
    def format_resume(self, resume: Resume, output_path=None) -> str:
        """
        Format a resume as HTML using the specified template.
        
        Args:
            resume: The Resume object to format
            output_path: Optional file path to save the HTML
            
        Returns:
            The formatted HTML as a string
        """
        try:
            template = self.env.get_template(self.template_name)
        except Exception as e:
            print(f"Error loading template {self.template_name}: {str(e)}")
            print("Falling back to harvard.html template")
            template = self.env.get_template("harvard.html")
            
        html_content = template.render(resume=resume)
        
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        
        return html_content