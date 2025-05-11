# Resume Builder & Optimizer

A powerful AI-powered tool that helps you optimize your resume for specific job descriptions. This application uses advanced natural language processing to analyze your resume and job descriptions, providing tailored recommendations and generating optimized versions of your resume.

## Features

- **Resume Parsing**: Automatically extracts information from your PDF resume
- **Job Description Analysis**: Analyzes job descriptions to identify key requirements and skills
- **ATS Optimization**: Optimizes your resume for Applicant Tracking Systems
- **Smart Resume Generation**: Creates tailored versions of your resume for specific job applications
- **Multiple Output Formats**: Supports PDF, HTML, and JSON output formats
- **Template Support**: Multiple professional resume templates available
- **Keyword Optimization**: Helps incorporate relevant keywords from job descriptions

## Prerequisites

- Python 3.11 or higher
- Google API key (for Gemini AI)
- System dependencies (for PDF processing):
  - libpango-1.0-0
  - libharfbuzz0b
  - libpangoft2-1.0-0
  - libffi-dev

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-builder.git
cd resume-builder
```

2. Install system dependencies (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libffi-dev
```

3. Install Python dependencies using `uv`:
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

4. Set up your Google API key:
   - Create a `.env` file in the project root
   - Add your API key: `GOOGLE_API_KEY=your_api_key_here`

## Running the Application

1. Start the Streamlit web interface:
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the application
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Follow the on-screen instructions:
   - Enter your Google API key
   - Upload your resume (PDF format)
   - Paste the job description
   - Choose output format
   - Click "Generate Optimized Resume"

## Project Structure

```

## Dependencies

The project uses several key dependencies:
- streamlit>=1.45.0
- langchain>=0.3.19
- langchain-google-genai>=2.0.11
- weasyprint>=64.1
- jinja2>=3.1.5
- pypdf>=5.3.0
- And more (see pyproject.toml for full list)

## Troubleshooting

### Common Issues

1. **Missing System Dependencies**
   If you encounter errors related to PDF processing, ensure all system dependencies are installed:
   ```bash
   sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libffi-dev
   ```

2. **Google API Key Issues**
   - Ensure your API key is correctly set in the `.env` file
   - Verify the API key has access to the Gemini API
   - Check if you've exceeded your API quota

3. **PDF Processing Errors**
   - Ensure your PDF is not password-protected
   - Check if the PDF is readable and not corrupted
   - Verify all system dependencies are installed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please open an issue in the GitHub repository.