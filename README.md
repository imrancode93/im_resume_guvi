# AI Resume Tailoring Assistant

An intelligent resume tailoring assistant built with LangChain and Streamlit that helps users optimize their resumes for specific job descriptions.

## Features

- Resume and job description analysis
- Gap analysis between resume and job requirements
- Automated resume tailoring
- Personalized cover letter generation
- ATS optimization
- Fit evaluation
- Downloadable results

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   MODEL_NAME=gpt-4-turbo-preview
   TEMPERATURE=0.7
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open the application in your browser
2. Paste your resume and the target job description
3. Click "Generate Tailored Content"
4. Review the AI-generated analyses and content
5. Download the results for your job application

## Tech Stack

- Streamlit: Web interface
- LangChain: AI agent orchestration
- OpenAI GPT: Language understanding and generation
- Python-dotenv: Environment variable management

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── agents/            # LangChain agents
│   ├── __init__.py
│   ├── resume_agent.py
│   └── cover_letter_agent.py
├── utils/             # Utility functions
│   ├── __init__.py
│   ├── text_processor.py
│   └── file_handler.py
├── requirements.txt   # Project dependencies
└── .env              # Environment variables (not tracked in git)
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4-turbo-preview
TEMPERATURE=0.7
```

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `MODEL_NAME`: The OpenAI model to use (default: gpt-4-turbo-preview)
- `TEMPERATURE`: Model temperature for generation (default: 0.7)

## License

MIT License 