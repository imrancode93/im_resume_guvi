import os
import subprocess
import sys
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up."""
    try:
        # Check if virtual environment is activated (venv or conda)
        in_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            os.environ.get("CONDA_DEFAULT_ENV") is not None
        )
        if not in_venv:
            print("Error: Virtual environment is not activated!")
            print("Please activate your environment first:")
            print("On Windows: venv\\Scripts\\activate or conda activate <env>")
            print("On Unix/Linux/MacOS: source venv/bin/activate or conda activate <env>")
            return False
        
        # Check if .env file exists and has API key
        env_file = Path(".env")
        if not env_file.exists():
            print("Error: .env file not found!")
            print("Please run setup.py first to create the .env file.")
            return False
        
        with open(env_file) as f:
            env_content = f.read()
            if "your_api_key_here" in env_content or "OPENAI_API_KEY=" not in env_content:
                print("Error: Please update the OPENAI_API_KEY in .env file!")
                return False
        
        return True
    except Exception as e:
        print(f"Environment check failed: {e}")
        return False

def run_application():
    """Run the Streamlit application."""
    try:
        if check_environment():
            print("Starting the application...")
            subprocess.run(["streamlit", "run", "app.py"])
        else:
            sys.exit(1)
    except Exception as e:
        print(f"Failed to start the application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        run_application()
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1) 