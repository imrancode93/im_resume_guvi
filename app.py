import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory
import json
from utils.file_handler import FileHandler
from agents.resume_agent import ResumeAgent
from agents.cover_letter_agent import CoverLetterAgent
from io import BytesIO

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="AI Resume Tailoring Assistant",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'cover_letter' not in st.session_state:
    st.session_state.cover_letter = None
if 'raw_llm_output' not in st.session_state:
    st.session_state.raw_llm_output = {}

def initialize_llm():
    """Initialize the language model."""
    return ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )

def make_serializable(obj):
    """Recursively convert objects to serializable types for JSON serialization."""
    if isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif hasattr(obj, "content"):  # For LangChain message objects
        return str(obj.content)
    else:
        try:
            json.dumps(obj)
            return obj
        except TypeError:
            return str(obj)

def create_cover_letter_doc(cover_letter: str) -> BytesIO:
    """Create a Word document in memory for the cover letter."""
    from docx import Document
    doc = Document()
    doc.add_paragraph(cover_letter)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def main():
    """Main Streamlit app logic."""
    st.title("AI Resume Tailoring Assistant")
    st.write("Optimize your resume for specific job descriptions using AI")

    # Input sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Resume")
        resume_text = st.text_area(
            "Paste your resume here",
            height=300,
            help="Paste your resume content here"
        )
    
    with col2:
        st.subheader("Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=300,
            help="Paste the job description here"
        )

    # Debug toggle
    show_debug = st.sidebar.checkbox("Show raw LLM output (debug)")

    # Generate button
    if st.button("Generate Tailored Content", type="primary"):
        if not resume_text or not job_description:
            st.error("Please provide both resume and job description")
            return

        with st.spinner("Analyzing and generating content..."):
            try:
                llm = initialize_llm()
                resume_agent = ResumeAgent(llm)
                result = resume_agent.analyze_resume(resume_text, job_description)
                st.session_state.analysis_results = result
                st.session_state.raw_llm_output['resume'] = result
                # Generate cover letter
                cover_letter_agent = CoverLetterAgent(llm)
                cover_letter_result = cover_letter_agent._generate_cover_letter(resume_text, job_description)
                st.session_state.cover_letter = cover_letter_result.get("cover_letter", "")
                st.session_state.raw_llm_output['cover_letter'] = cover_letter_result
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                return

    # Display results if available
    if st.session_state.analysis_results:
        st.subheader("Analysis Results")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "Resume Analysis",
            "Job Analysis",
            "Cover Letter",
            "Fit Evaluation"
        ])
        
        with tab1:
            st.write("Resume Analysis Results")
            results = st.session_state.analysis_results

            # Skills Analysis
            skills = results.get("skills_analysis", {})
            st.subheader("Skills Analysis")
            st.write("Technical Skills:", skills.get("technical_skills", []))
            st.write("Soft Skills:", skills.get("soft_skills", []))
            st.write("Tools & Technologies:", skills.get("tools_and_technologies", []))

            # Experience Analysis
            st.subheader("Experience Analysis")
            for exp in results.get("experience_analysis", []):
                st.markdown(f"**{exp.get('title', '')} at {exp.get('company', '')}** ({exp.get('dates', '')})")
                for resp in exp.get("responsibilities", []):
                    st.write("-", resp)

            # Tailored Bullets
            st.subheader("Tailored Bullet Points")
            for bullet in results.get("tailored_bullets", []):
                st.write("-", bullet)

            # Strengths and Areas for Improvement
            fit = results.get("fit_analysis", {})
            st.subheader("Strengths")
            for s in fit.get("strengths", []):
                st.write("-", s)
            st.subheader("Areas for Improvement")
            for a in fit.get("areas_for_improvement", []):
                st.write("-", a)

        with tab2:
            st.write("Job Analysis Results")
            job = results.get("job_requirements", {})
            st.subheader("Required Skills")
            st.write(job.get("required_skills", []))
            st.subheader("Preferred Skills")
            st.write(job.get("preferred_skills", []))
            st.subheader("Responsibilities")
            st.write(job.get("responsibilities", []))
            st.subheader("Qualifications")
            st.write(job.get("qualifications", []))

        with tab3:
            # Show the generated cover letter
            cover_letter = st.session_state.cover_letter
            if cover_letter:
                st.subheader("Generated Cover Letter")
                st.write(cover_letter)
                # Download button for cover letter only (in-memory)
                word_buffer = create_cover_letter_doc(cover_letter)
                st.download_button(
                    label="Download Cover Letter as Word",
                    data=word_buffer,
                    file_name="cover_letter.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.info("No cover letter generated yet.")

        with tab4:
            st.write("Fit Evaluation")
            st.subheader("Fit Score")
            st.write("Overall Score:", fit.get("overall_score", ""))
            st.write("Skills Match:", fit.get("skills_match", ""))
            st.write("Experience Match:", fit.get("experience_match", ""))
            st.subheader("Missing Requirements")
            st.write(fit.get("missing_requirements", []))
            st.subheader("Strengths")
            st.write(fit.get("strengths", []))
            st.subheader("Areas for Improvement")
            st.write(fit.get("areas_for_improvement", []))

    # Show warnings if results are empty
    if st.session_state.analysis_results is None:
        st.warning("No analysis results found. Please check your input or try again.")
    if st.session_state.cover_letter is None:
        st.warning("No cover letter generated. Please check your input or try again.")

    # Debug output
    if show_debug:
        st.subheader("Raw LLM Output (Debug)")
        st.write(st.session_state.raw_llm_output)

if __name__ == "__main__":
    main() 