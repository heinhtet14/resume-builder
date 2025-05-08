import streamlit as st
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from resume_builder.tools.resume_parser import ResumeParser
from resume_builder.tools.job_analyzer import JobDescriptionAnalyzer
from resume_builder.tools.resume_generator import ResumeGenerator
from resume_builder.tools.ats_optimizer import ATSOptimizer
from resume_builder.formatters.html_formatter import HtmlFormatter
from resume_builder.formatters.pdf_converter import PdfConverter

# Load environment variables
load_dotenv()

def set_api_key(api_key=None):
    """Set the Google API key from various sources in order of priority."""
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        return api_key
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Google API key not found. Please set the GOOGLE_API_KEY environment variable")
    
    return api_key

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Resume Builder & Optimizer",
        page_icon="📄",
        layout="wide"
    )
    
    # Title and description
    st.title("Resume Builder & Optimizer")
    st.markdown("""
    This tool helps you optimize your resume for specific job descriptions.
    Upload your resume, paste the job description, and get an optimized version!
    """)
    
    # Sidebar for API key input
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Google API Key", type="password")
        if not api_key:
            st.warning("Please enter your Google API key to continue")
            return
        
        set_api_key(api_key)
        
        # Add helpful information in sidebar
        st.markdown("---")
        st.markdown("### How to use:")
        st.markdown("""
        1. Enter your Google API key
        2. Upload your resume (PDF)
        3. Paste the job description
        4. Choose output format
        5. Click 'Generate Optimized Resume'
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File uploader for resume
        uploaded_resume = st.file_uploader(
            "Upload your resume (PDF)",
            type=['pdf'],
            help="Upload your current resume in PDF format"
        )
        
        # Text area for job description
        job_description = st.text_area(
            "Paste the job description here",
            height=200,
            help="Copy and paste the full job description here"
        )
    
    with col2:
        # Options
        st.subheader("Options")
        output_format = st.selectbox(
            "Output Format",
            ["PDF", "HTML", "JSON"],
            help="Choose the format for your optimized resume"
        )
        
        skip_ats = st.checkbox(
            "Skip ATS Optimization",
            help="Skip the ATS (Applicant Tracking System) optimization step"
        )
        
        # Template selection (if available)
        st.markdown("---")
        st.subheader("Resume Template")
        template_options = ["Modern", "Professional", "Creative"]
        selected_template = st.selectbox(
            "Choose a template",
            template_options,
            help="Select a template style for your resume"
        )
    
    # Process button
    if st.button("Generate Optimized Resume", type="primary"):
        if not uploaded_resume or not job_description:
            st.error("Please upload a resume and provide a job description")
            return
        
        try:
            # Create output directory
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save uploaded resume
            resume_path = os.path.join(output_dir, "uploaded_resume.pdf")
            with open(resume_path, "wb") as f:
                f.write(uploaded_resume.getvalue())
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("Processing your resume..."):
                # Parse resume
                status_text.text("Parsing resume...")
                resume_parser = ResumeParser(api_key=api_key)
                resume = resume_parser(resume_path)
                progress_bar.progress(25)
                
                # Analyze job description
                status_text.text("Analyzing job description...")
                job_analyzer = JobDescriptionAnalyzer(api_key=api_key)
                job = job_analyzer(job_description)
                progress_bar.progress(50)
                
                # Generate optimized resume
                status_text.text("Generating optimized resume...")
                resume_generator = ResumeGenerator(api_key=api_key)
                optimized_resume = resume_generator(resume, job)
                progress_bar.progress(75)
                
                # ATS optimization
                if not skip_ats:
                    status_text.text("Optimizing for ATS...")
                    ats_optimizer = ATSOptimizer(api_key=api_key)
                    optimized_resume = ats_optimizer(optimized_resume, job)
                
                # Generate output
                status_text.text("Generating final output...")
                if output_format in ['HTML', 'PDF']:
                    html_formatter = HtmlFormatter()
                    html_path = os.path.join(output_dir, "resume.html")
                    html_content = html_formatter.format_resume(optimized_resume, html_path)
                    
                    if output_format == 'PDF':
                        pdf_converter = PdfConverter()
                        output_path = pdf_converter.convert_html_to_pdf(
                            html_file=html_path,
                            output_path=os.path.join(output_dir, "resume.pdf")
                        )
                    else:
                        output_path = html_path
                else:
                    output_path = os.path.join(output_dir, "resume.json")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(optimized_resume.model_dump(), f, indent=2)
                
                progress_bar.progress(100)
                status_text.text("Complete!")
                
                st.success("Resume optimization complete!")
                
                # Provide download button
                with open(output_path, "rb") as file:
                    st.download_button(
                        label=f"Download {output_format} Resume",
                        data=file,
                        file_name=f"optimized_resume.{output_format.lower()}",
                        mime=f"application/{output_format.lower()}"
                    )
                
                # Show preview if HTML
                if output_format == 'HTML':
                    st.subheader("Preview")
                    st.components.v1.iframe(html_path, height=600)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)

if __name__ == "__main__":
    main() 