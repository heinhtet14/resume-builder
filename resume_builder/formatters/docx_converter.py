# New file: resume_builder/formatters/docx_converter.py

import os
import subprocess
import sys
from pathlib import Path
import tempfile
import shutil

class DocxConverter:
    """Convert HTML to DOCX format using Python libraries with Pandoc fallback."""
    
    def __init__(self):
        """Initialize the converter and check if pandoc is installed."""
        try:
            self.pandoc_available = self._check_pandoc_installed()
        except (subprocess.SubprocessError, FileNotFoundError, PermissionError):
            print("Note: Pandoc is not available. Will use Python-based DOCX conversion.")
            self.pandoc_available = False
    
    def _check_pandoc_installed(self) -> bool:
        """Check if pandoc is installed and available in PATH."""
        try:
            # Try with shell=True for better cross-platform compatibility
            subprocess.run("pandoc --version", shell=True, check=True, 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Pandoc is available and will be used for DOCX conversion.")
            return True
        except Exception:
            return False
    
    def _convert_with_pandoc(self, html_file: str, output_path: str) -> bool:
        """Convert HTML to DOCX using Pandoc."""
        try:
            # Use shell=True for better cross-platform compatibility
            cmd = f'pandoc "{html_file}" -f html -t docx -o "{output_path}"'
            subprocess.run(cmd, shell=True, check=True, 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception as e:
            print(f"Error converting to DOCX with Pandoc: {str(e)}")
            return False
    
    def _convert_with_python(self, html_file: str, output_path: str) -> bool:
        """
        Convert HTML to DOCX using python-docx and html2docx.
        This is a fallback method if Pandoc is not available.
        """
        try:
            # Try to dynamically import the required packages
            try:
                from html2docx import html2docx
            except ImportError:
                print("Required packages for DOCX conversion are not installed.")
                print("Attempting to install them now...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "python-docx", "html2docx"],
                                  check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    from html2docx import html2docx
                    print("Successfully installed required packages.")
                except Exception as install_err:
                    print(f"Failed to install required packages: {str(install_err)}")
                    print("To use Python-based DOCX conversion, please install manually:")
                    print("pip install python-docx html2docx")
                    return False
            
            # Convert HTML to DOCX
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            html2docx(html_content, output_path)
            return True
        except ImportError:
            print("Error: html2docx or python-docx package not installed.")
            print("To use Python-based DOCX conversion, install required packages:")
            print("pip install python-docx html2docx")
            return False
        except Exception as e:
            print(f"Error converting to DOCX with Python: {str(e)}")
            return False
    
    def convert_html_to_docx(self, html_content=None, html_file=None, output_path=None) -> str:
        """
        Convert HTML to DOCX format.
        
        Args:
            html_content: HTML content as a string
            html_file: Path to an HTML file
            output_path: Path to save the DOCX
            
        Returns:
            The path to the generated DOCX file, or None if conversion failed
        """
        if html_content is None and html_file is None:
            raise ValueError("Either html_content or html_file must be provided")
        
        if output_path is None:
            if html_file:
                output_path = os.path.splitext(html_file)[0] + ".docx"
            else:
                output_path = "resume.docx"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # If we have HTML content but no file, write to a temporary file
        temp_dir = None
        created_html_file = False
        if html_file is None:
            temp_dir = tempfile.mkdtemp()
            html_file = os.path.join(temp_dir, "temp.html")
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            created_html_file = True
        
        try:
            success = False
            
            # Try Pandoc first if available
            if self.pandoc_available:
                print("Attempting to convert with Pandoc...")
                success = self._convert_with_pandoc(html_file, output_path)
            
            # Fall back to Python-based conversion if Pandoc fails or isn't available
            if not success:
                print("Attempting to convert with Python libraries...")
                success = self._convert_with_python(html_file, output_path)
            
            if success:
                print(f"Successfully converted HTML to DOCX: {output_path}")
                return output_path
            else:
                print("Failed to convert HTML to DOCX. Try installing Pandoc or the required Python packages.")
                return None
                
        finally:
            # Clean up temporary directory if we created one
            if temp_dir and created_html_file:
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception:
                    pass  # Ignore cleanup errors