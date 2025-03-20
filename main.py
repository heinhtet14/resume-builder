# import os
# import json
# import argparse
# from pathlib import Path
# from dotenv import load_dotenv

# from resume_builder.agent.react_agent import create_resume_agent
# from resume_builder.agent.ats_agent import create_ats_optimization_agent
# from resume_builder.tools.resume_parser import ResumeParser
# from resume_builder.tools.job_analyzer import JobDescriptionAnalyzer
# from resume_builder.tools.resume_generator import ResumeGenerator
# from resume_builder.tools.ats_optimizer import ATSOptimizer
# from resume_builder.formatters.html_formatter import HtmlFormatter
# from resume_builder.formatters.pdf_converter import PdfConverter

# # Load environment variables from .env file
# load_dotenv()

# def set_api_key(api_key=None):
#     """Set the Google API key from various sources in order of priority."""
#     if api_key:
#         os.environ["GOOGLE_API_KEY"] = api_key
#         return api_key
    
#     # Check if already in environment (could be from .env file)
#     api_key = os.environ.get("GOOGLE_API_KEY")
#     if not api_key:
#         # Try to read from a file
#         key_file = os.path.join(os.path.expanduser("~"), ".google_api_key")
#         if os.path.exists(key_file):
#             with open(key_file, 'r') as f:
#                 api_key = f.read().strip()
#                 os.environ["GOOGLE_API_KEY"] = api_key
    
#     if not api_key:
#         raise ValueError("Google API key not found. Please set the GOOGLE_API_KEY environment variable in a .env file, or provide it with --api-key")
    
#     return api_key

# def save_json(data, file_path):
#     """Save data as JSON to a file."""
#     with open(file_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=2)

# def optimize_resume(resume_file_path, job_description, output_format='pdf', output_dir='output', api_key=None, skip_ats=False):
#     """
#     Optimize a resume for a specific job description.
    
#     Args:
#         resume_file_path: Path to the PDF resume file
#         job_description: The job description text
#         output_format: Output format ('pdf', 'html', or 'json')
#         output_dir: Directory to save output files
#         api_key: Google API key for Gemini
#         skip_ats: Skip the ATS optimization step if True
        
#     Returns:
#         Path to the generated output file
#     """
#     # Set API key
#     api_key = set_api_key(api_key)
    
#     print("Parsing resume...")
#     resume_parser = ResumeParser(api_key=api_key)
#     resume = resume_parser(resume_file_path)
    
#     print("Analyzing job description...")
#     job_analyzer = JobDescriptionAnalyzer(api_key=api_key)
#     job = job_analyzer(job_description)
    
#     print("Generating optimized resume...")
#     resume_generator = ResumeGenerator(api_key=api_key)
#     optimized_resume = resume_generator(resume, job)
    
#     # Create output directory if it doesn't exist
#     os.makedirs(output_dir, exist_ok=True)
    
#     # Save initial optimized resume JSON for reference
#     initial_json_path = os.path.join(output_dir, "initial_resume.json")
#     save_json(optimized_resume.model_dump(), initial_json_path)
#     print(f"Initial optimized resume JSON saved to: {initial_json_path}")
    
#     # ATS optimization step
#     if not skip_ats:
#         print("\nOptimizing for ATS...")
#         ats_optimizer = ATSOptimizer(api_key=api_key)
#         optimized_resume = ats_optimizer(optimized_resume, job)
    
#     # Save final resume JSON
#     json_path = os.path.join(output_dir, "resume.json")
#     save_json(optimized_resume.model_dump(), json_path)
#     print(f"Final resume JSON saved to: {json_path}")
    
#     if output_format in ['html', 'pdf']:
#         # Generate HTML
#         html_formatter = HtmlFormatter()
#         html_path = os.path.join(output_dir, "resume.html")
#         html_content = html_formatter.format_resume(optimized_resume, html_path)
#         print(f"Resume HTML saved to: {html_path}")
        
#         if output_format == 'pdf':
#             # Convert HTML to PDF
#             pdf_converter = PdfConverter()
#             pdf_path = pdf_converter.convert_html_to_pdf(html_file=html_path, 
#                                                      output_path=os.path.join(output_dir, "resume.pdf"))
#             print(f"Resume PDF saved to: {pdf_path}")
#             return pdf_path
#         return html_path
    
#     return json_path

# def parse_command_line_args():
#     """Parse command line arguments."""
#     parser = argparse.ArgumentParser(description="Resume Builder")
#     parser.add_argument("--resume", required=True, help="Path to the resume PDF file")
#     parser.add_argument("--job", required=True, help="Path to the job description text file")
#     parser.add_argument("--format", choices=["pdf", "html", "json"], default="pdf", 
#                         help="Output format (pdf, html, or json)")
#     parser.add_argument("--output-dir", default="output", help="Directory to save output files")
#     parser.add_argument("--mode", choices=["direct", "agent"], default="direct",
#                         help="Running mode (direct or agent-based)")
#     parser.add_argument("--api-key", help="Google API key for Gemini (optional if set in environment or .env file)")
#     parser.add_argument("--skip-ats", action="store_true", help="Skip the ATS optimization step")
    
#     return parser.parse_args()

# def main():
#     """Direct mode for resume optimization."""
#     args = parse_command_line_args()
    
#     # Read job description from file
#     with open(args.job, 'r', encoding='utf-8') as f:
#         job_description = f.read()
    
#     # Optimize resume
#     output_path = optimize_resume(
#         resume_file_path=args.resume,
#         job_description=job_description,
#         output_format=args.format,
#         output_dir=args.output_dir,
#         api_key=args.api_key,
#         skip_ats=args.skip_ats
#     )
    
#     print(f"\nResume optimization complete! Output saved to: {output_path}")

# def run_with_agent(args):
#     """Run the resume optimizer using the ReAct agent."""
#     # Set API key
#     api_key = set_api_key(args.api_key)
    
#     # Read job description from file
#     with open(args.job, 'r', encoding='utf-8') as f:
#         job_description = f.read()
    
#     # Create resume agent
#     resume_agent = create_resume_agent(model_name="gemini-1.5-pro", verbose=True, api_key=api_key)
    
#     # Run resume agent
#     print("\nRunning Resume Builder Agent...")
#     result = resume_agent.invoke({
#         "input": f"I have a resume file at {args.resume} and I'm applying for a job with this description: {job_description}. Please help me create a tailored resume for this job."
#     })
    
#     print("\nResume Builder Agent complete!")
    
#     try:
#         # Parse the resume and job
#         resume_parser = ResumeParser(api_key=api_key)
#         resume = resume_parser(args.resume)
        
#         job_analyzer = JobDescriptionAnalyzer(api_key=api_key)
#         job = job_analyzer(job_description)
        
#         resume_generator = ResumeGenerator(api_key=api_key)
#         initial_resume = resume_generator(resume, job)
        
#         # Save initial resume
#         os.makedirs(args.output_dir, exist_ok=True)
#         initial_json_path = os.path.join(args.output_dir, "initial_resume.json")
#         save_json(initial_resume.model_dump(), initial_json_path)
        
#         # Run ATS optimization if not skipped
#         if not args.skip_ats:
#             print("\nRunning ATS Optimization Agent...")
#             ats_agent = create_ats_optimization_agent(model_name="gemini-1.5-pro", verbose=True, api_key=api_key)
            
#             ats_result = ats_agent.invoke({
#                 "input": f"I have a resume that I need to optimize for ATS systems. The job description is: {job_description}"
#             })
            
#             print("\nATS Optimization Agent complete!")
            
#             # Use the ATSOptimizer tool directly as fallback in case the agent doesn't use it correctly
#             ats_optimizer = ATSOptimizer(api_key=api_key)
#             optimized_resume = ats_optimizer(initial_resume, job)
#         else:
#             optimized_resume = initial_resume
        
#         # Generate HTML and PDF
#         os.makedirs(args.output_dir, exist_ok=True)
        
#         html_formatter = HtmlFormatter()
#         html_path = os.path.join(args.output_dir, "resume.html")
#         html_formatter.format_resume(optimized_resume, html_path)
        
#         # Generate the requested format
#         if args.format == "pdf":
#             pdf_converter = PdfConverter()
#             output_path = pdf_converter.convert_html_to_pdf(
#                 html_file=html_path,
#                 output_path=os.path.join(args.output_dir, "resume.pdf")
#             )
#             print(f"\nResume PDF saved to: {output_path}")
#         elif args.format == "html":
#             print(f"\nResume HTML saved to: {html_path}")
#         else:  # json
#             json_path = os.path.join(args.output_dir, "resume.json")
#             save_json(optimized_resume.model_dump(), json_path)
#             print(f"\nResume JSON saved to: {json_path}")
    
#     except Exception as e:
#         print(f"Error generating output: {str(e)}")
#         print("Please check the agent's response for details.")

# if __name__ == "__main__":
#     print("Resume Builder")
#     print("==============")
    
#     args = parse_command_line_args()
    
#     if args.mode == "agent":
#         run_with_agent(args)
#     else:
#         main()

import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

from resume_builder.agent.react_agent import create_resume_agent
from resume_builder.agent.ats_agent import create_ats_optimization_agent
from resume_builder.tools.resume_parser import ResumeParser
from resume_builder.tools.job_analyzer import JobDescriptionAnalyzer
from resume_builder.tools.resume_generator import ResumeGenerator
from resume_builder.tools.ats_optimizer import ATSOptimizer
from resume_builder.formatters.html_formatter import HtmlFormatter
from resume_builder.formatters.pdf_converter import PdfConverter
from resume_builder.formatters.docx_converter import DocxConverter
from resume_builder.formatters.template_manager import TemplateManager

# Load environment variables from .env file
load_dotenv()

def set_api_key(api_key=None):
    """Set the Google API key from various sources in order of priority."""
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        return api_key
    
    # Check if already in environment (could be from .env file)
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # Try to read from a file
        key_file = os.path.join(os.path.expanduser("~"), ".google_api_key")
        if os.path.exists(key_file):
            with open(key_file, 'r') as f:
                api_key = f.read().strip()
                os.environ["GOOGLE_API_KEY"] = api_key
    
    if not api_key:
        raise ValueError("Google API key not found. Please set the GOOGLE_API_KEY environment variable in a .env file, or provide it with --api-key")
    
    return api_key

def save_json(data, file_path):
    """Save data as JSON to a file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def optimize_resume(resume_file_path, job_description, output_format='pdf', output_dir='output', 
                   api_key=None, skip_ats=False, template_name=None, user_keywords=None):
    """
    Optimize a resume for a specific job description.
    
    Args:
        resume_file_path: Path to the PDF resume file
        job_description: The job description text
        output_format: Output format ('pdf', 'html', 'docx', or 'json')
        output_dir: Directory to save output files
        api_key: Google API key for Gemini
        skip_ats: Skip the ATS optimization step if True
        template_name: Name of the template to use (optional)
        user_keywords: List of keywords provided by the user (optional)
        
    Returns:
        Path to the generated output file
    """
    # Set API key
    api_key = set_api_key(api_key)
    
    print("Parsing resume...")
    resume_parser = ResumeParser(api_key=api_key)
    resume = resume_parser(resume_file_path)
    
    print("Analyzing job description...")
    job_analyzer = JobDescriptionAnalyzer(api_key=api_key)
    job = job_analyzer(job_description)
    
    # Process user keywords if provided
    selected_keywords = []
    if user_keywords and len(user_keywords) > 0:
        from resume_builder.tools.keyword_processor import KeywordProcessor
        keyword_processor = KeywordProcessor()
        selected_keywords = keyword_processor({
            'keywords': user_keywords,
            'max_count': 10,
            'job': job
        })
        print(f"Selected keywords: {', '.join(selected_keywords)}")
    
    print("Generating optimized resume...")
    resume_generator = ResumeGenerator(api_key=api_key)
    optimized_resume = resume_generator({
        'resume': resume, 
        'job': job,
        'keywords': selected_keywords
    })
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save initial optimized resume JSON for reference
    initial_json_path = os.path.join(output_dir, "initial_resume.json")
    save_json(optimized_resume.model_dump(), initial_json_path)
    print(f"Initial optimized resume JSON saved to: {initial_json_path}")
    
    # ATS optimization step
    if not skip_ats:
        print("\nOptimizing for ATS...")
        ats_optimizer = ATSOptimizer(api_key=api_key)
        optimized_resume = ats_optimizer(optimized_resume, job)
    
    # Save final resume JSON
    json_path = os.path.join(output_dir, "resume.json")
    save_json(optimized_resume.model_dump(), json_path)
    print(f"Final resume JSON saved to: {json_path}")
    
    if output_format in ['html', 'pdf', 'docx']:
        # Initialize template manager and get template
        template_manager = TemplateManager()
        
        # Use specified template or default to Harvard
        template_filename = None
        if template_name:
            template_filename = template_manager.get_template_filename(template_name)
        
        if not template_filename:
            template_filename = "harvard.html"  # Default template
        
        # Generate HTML
        html_formatter = HtmlFormatter(template_name=template_filename)
        html_path = os.path.join(output_dir, "resume.html")
        html_content = html_formatter.format_resume(optimized_resume, html_path)
        print(f"Resume HTML saved to: {html_path}")
        
        if output_format == 'pdf':
            # Convert HTML to PDF
            pdf_converter = PdfConverter()
            pdf_path = pdf_converter.convert_html_to_pdf(
                html_file=html_path, 
                output_path=os.path.join(output_dir, "resume.pdf")
            )
            print(f"Resume PDF saved to: {pdf_path}")
            return pdf_path
        elif output_format == 'docx':
            # Convert HTML to DOCX
            docx_converter = DocxConverter()
            docx_path = docx_converter.convert_html_to_docx(
                html_file=html_path,
                output_path=os.path.join(output_dir, "resume.docx")
            )
            print(f"Resume DOCX saved to: {docx_path}")
            return docx_path
        
        return html_path
    
    return json_path

def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Resume Builder")
    
    # Create argument groups
    required_args = parser.add_argument_group('required arguments')
    optional_args = parser.add_argument_group('optional arguments')
    
    # Required arguments (except when listing templates)
    required_args.add_argument("--resume", help="Path to the resume PDF file")
    required_args.add_argument("--job", help="Path to the job description text file")
    
    # Optional arguments
    optional_args.add_argument("--format", choices=["pdf", "html", "docx", "json"], default="pdf", 
                        help="Output format (pdf, html, docx, or json)")
    optional_args.add_argument("--output-dir", default="output", help="Directory to save output files")
    optional_args.add_argument("--mode", choices=["direct", "agent"], default="direct",
                        help="Running mode (direct or agent-based)")
    optional_args.add_argument("--api-key", help="Google API key for Gemini (optional if set in environment or .env file)")
    optional_args.add_argument("--skip-ats", action="store_true", help="Skip the ATS optimization step")
    optional_args.add_argument("--template", help="Template name to use for resume formatting")
    optional_args.add_argument("--keywords", nargs="+", help="Keywords to include in the resume (space-separated)")
    optional_args.add_argument("--list-templates", action="store_true", help="List available resume templates and exit")
    
    args = parser.parse_args()
    
    # Check if required arguments are missing when not listing templates
    if not args.list_templates and (args.resume is None or args.job is None):
        if args.resume is None:
            parser.error("the --resume argument is required unless using --list-templates")
        if args.job is None:
            parser.error("the --job argument is required unless using --list-templates")
    
    return args
# Modified function in main.py

def list_available_templates():
    """List available templates and exit."""
    print("\nListing available resume templates...")
    template_manager = TemplateManager()
    templates = template_manager.get_template_list()
    
    print("\nAvailable Resume Templates:")
    print("==========================")
    if templates:
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template}")
        print("\nUse --template \"Template Name\" to specify a template.")
    else:
        print("No templates found. Please make sure the templates directory exists and contains HTML templates.")
        print(f"Expected template directory: {template_manager.template_dir}")
        
        # List files in the project root to help debug
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print(f"\nProject root directory: {base_dir}")
            print("Contents of project root:")
            for item in os.listdir(base_dir):
                print(f"- {item}")
                
            # Check if templates directory exists
            templates_dir = os.path.join(base_dir, "templates")
            if os.path.exists(templates_dir):
                print(f"\nContents of templates directory:")
                for item in os.listdir(templates_dir):
                    print(f"- {item}")
        except Exception as e:
            print(f"Error listing directories: {str(e)}")
            
def main():
    """Direct mode for resume optimization."""
    args = parse_command_line_args()
    
    # Check if we should just list templates and exit
    if args.list_templates:
        list_available_templates()
        return
    
    # Read job description from file
    with open(args.job, 'r', encoding='utf-8') as f:
        job_description = f.read()
    
    # Optimize resume
    output_path = optimize_resume(
        resume_file_path=args.resume,
        job_description=job_description,
        output_format=args.format,
        output_dir=args.output_dir,
        api_key=args.api_key,
        skip_ats=args.skip_ats,
        template_name=args.template,
        user_keywords=args.keywords
    )
    
    print(f"\nResume optimization complete! Output saved to: {output_path}")

def run_with_agent(args):
    """Run the resume optimizer using the ReAct agent."""
    # Set API key
    api_key = set_api_key(args.api_key)
    
    # Read job description from file
    with open(args.job, 'r', encoding='utf-8') as f:
        job_description = f.read()
    
    # Build the prompt with any additional user requirements
    prompt = f"I have a resume file at {args.resume} and I'm applying for a job with this description: {job_description}."
    
    if args.keywords:
        keywords_str = ", ".join(args.keywords)
        prompt += f" Please include these keywords in my resume: {keywords_str}."
    
    prompt += " Please help me create a tailored resume for this job."
    
    # Create resume agent
    resume_agent = create_resume_agent(model_name="gemini-1.5-pro", verbose=True, api_key=api_key)
    
    # Run resume agent
    print("\nRunning Resume Builder Agent...")
    result = resume_agent.invoke({
        "input": prompt
    })
    
    print("\nResume Builder Agent complete!")
    
    try:
        # Parse the resume and job
        resume_parser = ResumeParser(api_key=api_key)
        resume = resume_parser(args.resume)
        
        job_analyzer = JobDescriptionAnalyzer(api_key=api_key)
        job = job_analyzer(job_description)
        
        # Process user keywords if provided
        selected_keywords = []
        if args.keywords and len(args.keywords) > 0:
            from resume_builder.tools.keyword_processor import KeywordProcessor
            keyword_processor = KeywordProcessor()
            selected_keywords = keyword_processor({
                'keywords': args.keywords,
                'max_count': 10,
                'job': job
            })
        
        # Generate initial resume
        resume_generator = ResumeGenerator(api_key=api_key)
        initial_resume = resume_generator({
            'resume': resume, 
            'job': job,
            'keywords': selected_keywords
        })
        
        # Save initial resume
        os.makedirs(args.output_dir, exist_ok=True)
        initial_json_path = os.path.join(args.output_dir, "initial_resume.json")
        save_json(initial_resume.model_dump(), initial_json_path)
        
        # Run ATS optimization if not skipped
        if not args.skip_ats:
            print("\nRunning ATS Optimization Agent...")
            ats_agent = create_ats_optimization_agent(model_name="gemini-1.5-pro", verbose=True, api_key=api_key)
            
            ats_result = ats_agent.invoke({
                "input": f"I have a resume that I need to optimize for ATS systems. The job description is: {job_description}"
            })
            
            print("\nATS Optimization Agent complete!")
            
            # Use the ATSOptimizer tool directly as fallback in case the agent doesn't use it correctly
            ats_optimizer = ATSOptimizer(api_key=api_key)
            optimized_resume = ats_optimizer(initial_resume, job)
        else:
            optimized_resume = initial_resume
        
        # Generate output files
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Initialize template manager and get template
        template_manager = TemplateManager()
        
        # Use specified template or default to Harvard
        template_filename = None
        if args.template:
            template_filename = template_manager.get_template_filename(args.template)
        
        if not template_filename:
            template_filename = "harvard.html"  # Default template
        
        # Generate HTML
        html_formatter = HtmlFormatter(template_name=template_filename)
        html_path = os.path.join(args.output_dir, "resume.html")
        html_formatter.format_resume(optimized_resume, html_path)
        
        # Generate the requested format
        if args.format == "pdf":
            pdf_converter = PdfConverter()
            output_path = pdf_converter.convert_html_to_pdf(
                html_file=html_path,
                output_path=os.path.join(args.output_dir, "resume.pdf")
            )
            print(f"\nResume PDF saved to: {output_path}")
        elif args.format == "docx":
            docx_converter = DocxConverter()
            output_path = docx_converter.convert_html_to_docx(
                html_file=html_path,
                output_path=os.path.join(args.output_dir, "resume.docx")
            )
            print(f"\nResume DOCX saved to: {output_path}")
        elif args.format == "html":
            print(f"\nResume HTML saved to: {html_path}")
        else:  # json
            json_path = os.path.join(args.output_dir, "resume.json")
            save_json(optimized_resume.model_dump(), json_path)
            print(f"\nResume JSON saved to: {json_path}")
    
    except Exception as e:
        print(f"Error generating output: {str(e)}")
        print("Please check the agent's response for details.")

if __name__ == "__main__":
    print("Resume Builder")
    print("==============")
    
    args = parse_command_line_args()
    
    if args.mode == "agent":
        run_with_agent(args)
    else:
        main()