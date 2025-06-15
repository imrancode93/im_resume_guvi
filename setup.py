import os
import subprocess
import sys
from pathlib import Path

def create_virtual_environment():
    """Create and activate virtual environment."""
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Get the path to the activate script
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
    else:  # Unix/Linux/MacOS
        activate_script = "venv/bin/activate"
    
    print(f"Virtual environment created. Activate it using:")
    print(f"On Windows: {activate_script}")
    print(f"On Unix/Linux/MacOS: source {activate_script}")

def install_requirements():
    """Install project requirements."""
    print("Installing requirements...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Requirements installed successfully.")

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        env_content = """OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4-turbo-preview
TEMPERATURE=0.7"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        print(".env file created. Please update OPENAI_API_KEY with your actual API key.")
    else:
        print(".env file already exists.")

def main():
    """Main setup function."""
    print("Starting project setup...")
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install requirements
    install_requirements()
    
    # Create .env file
    create_env_file()
    
    print("\nSetup completed!")
    print("\nTo run the project:")
    print("1. Activate the virtual environment")
    print("2. Update the OPENAI_API_KEY in .env file")
    print("3. Run: streamlit run app.py")

if __name__ == "__main__":
    main() 