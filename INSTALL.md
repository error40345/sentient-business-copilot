# Sentient Business Copilot - Installation Guide

## Overview
This is a professional AI-powered business planning application built with Streamlit and the ROMA framework.

## What's Included
- `app.py` - Main Streamlit application
- `agents/` - ROMA orchestrator for AI processing
- `config/` - Configuration files and profiles
- `services/` - PDF generation and other services
- `utils/` - Utility functions (state manager, config)
- `roma_dspy/` - ROMA framework core
- `.streamlit/` - Streamlit configuration
- `data/` - Runtime data directory
- `pyproject.toml` - Python dependencies
- `uv.lock` - Dependency lock file

## Installation

### Prerequisites
- Python 3.11 or higher
- pip or uv package manager

### Steps

1. **Extract the zip file**
   ```bash
   unzip sentient-business-copilot.zip
   cd sentient-business-copilot
   ```

2. **Install dependencies**
   
   Using uv (recommended):
   ```bash
   uv sync
   ```
   
   Or using pip:
   ```bash
   pip install -r pyproject.toml
   ```

3. **Set up environment variables**
   
   Create a `.env` file with the following:
   ```
   FIREWORKS_API_KEY=your_fireworks_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py --server.port 5000
   ```

5. **Access the application**
   Open your browser to: `http://localhost:5000`

## Features
- AI-powered business planning assistance
- Market research and analysis
- Financial projections
- Business plan PDF export
- Multi-stage business development guidance

## Support
For issues or questions, please refer to the README.md file.

## License
See LICENSE file for details.
