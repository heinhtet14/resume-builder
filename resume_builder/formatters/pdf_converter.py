import os
from weasyprint import HTML

class PdfConverter:
    """Convert HTML to PDF."""
    
    def convert_html_to_pdf(self, html_content=None, html_file=None, output_path=None):
        """
        Convert HTML to PDF.
        
        Args:
            html_content: HTML content as a string
            html_file: Path to an HTML file
            output_path: Path to save the PDF
            
        Returns:
            The path to the generated PDF
        """
        if html_content is None and html_file is None:
            raise ValueError("Either html_content or html_file must be provided")
        
        if output_path is None:
            if html_file:
                output_path = os.path.splitext(html_file)[0] + ".pdf"
            else:
                output_path = "resume.pdf"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        if html_file:
            HTML(filename=html_file).write_pdf(output_path)
        else:
            HTML(string=html_content).write_pdf(output_path)
        
        return output_path