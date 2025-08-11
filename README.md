# An LLM-Powered Financial Statement Analyzer 

This project aims to build a fast and efficient AI-powered financial statements analyzer to make financial reports easier to understand for everyone, helping users quickly gather key financial insights without reading lengthy documents. 
Users are able to upload the financial documents they want to analyze and select a role—beginner, financial analyst, or investor—based on their experience level. The analyzer demonstrates the key financial metrics and risk factors, while a built-in ChatBot allows users to ask questions about the documents, with responses tailored to their chosen role. In addition, to deal with the token limit issue, we added a simple toggle that lets users switch between APIs for more complete answers.

### Key Features
- 🤖 Q&A ChatBot - any financial statement related queries
- 📊 Financial Metrics Dashboard
- ⚠️ Risk Factors and Business Highlights Overview

## Directory Structure

```
cs7180_final_project/
├── README.md                  
├── requirements.txt           # Python dependencies
├── app.py                      
│
├── pages/                       
│   └── chatbot.py            # The page of chatbot
│
└── backend/                  # models and utilities
   ├── model_docling.py/     # RAG pipeline model (working) 
   ├── model_pdfplumber.py/  # RAG pipeline model (not working, using other pdf extraction method)
   └── utils.py/             # Functions for front end to back end interctions
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git
### Step 1: Clone the Repository
```bash
git clone https://github.com/rubingli001/cs7180_final_project.git
cd cs7180_final_project
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install required Python packages
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables
Create a `.env` file in the backend directory and add your API keys:

```bash
# Create .env file
touch .env

# Add the following content to .env file (replace with your actual API keys)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Quick Start

### Running the Application
```bash
# Run the Streamlit application
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`
