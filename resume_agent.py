from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List
import re
import json
import json5

# Helper to clean LLM output
def extract_json_with_key(text, required_key):
    """Extract the first JSON object containing the required key from the text, after stripping markdown code fences."""
    print("DEBUG: RAW LLM OUTPUT:", repr(text))
    # Remove markdown code fences if present
    text = re.sub(r"```(?:json)?\n?", "", text)
    text = re.sub(r"```", "", text)
    # Replace triple quotes with double quotes (just in case)
    text = re.sub(r'"""', '"', text)
    # Try to extract the largest JSON object
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        json_str = text[start:end+1]
        try:
            obj = json5.loads(json_str)
            if isinstance(obj, dict) and required_key in obj:
                print(f"DEBUG: Found JSON object with key '{required_key}'")
                return obj
        except Exception as e:
            print("DEBUG: Failed to parse JSON object:", e)
            print("DEBUG: JSON string that failed:", json_str)
    print(f"DEBUG: No JSON object with key '{required_key}' found!")
    return {}

class ResumeAgent:
    """Agent for analyzing and tailoring resumes using an LLM."""
    def __init__(self, llm):
        """Initialize with a language model."""
        self.llm = llm
        self.tools = self._create_tools()
        
    def _create_tools(self) -> List[Tool]:
        """Create specialized tools for resume analysis and tailoring."""
        return [
            Tool(
                name="extract_skills",
                func=self._extract_skills,
                description="Extracts skills from resume text"
            ),
            Tool(
                name="extract_experience",
                func=self._extract_experience,
                description="Extracts work experience from resume text"
            ),
            Tool(
                name="analyze_job_requirements",
                func=self._analyze_job_requirements,
                description="Analyzes job requirements from job description"
            ),
            Tool(
                name="generate_tailored_bullets",
                func=self._generate_tailored_bullets,
                description="Generates tailored bullet points for resume"
            ),
            Tool(
                name="calculate_fit_score",
                func=self._calculate_fit_score,
                description="Calculates fit score between resume and job"
            ),
            Tool(
                name="refine_analysis",
                func=self._refine_analysis,
                description="Refines the analysis results for better accuracy"
            )
        ]
    
    def _extract_skills(self, resume_text: str) -> Dict:
        """Extract skills from resume text."""
        prompt = ChatPromptTemplate.from_template(
            """Extract all technical and soft skills from the following resume text.\nReturn ONLY valid JSON, using double quotes for all keys and string values, and do not use triple quotes or multiline strings. Do not include markdown or explanations.\nThe JSON object MUST be wrapped in a 'skills_analysis' key as shown below.\n\nResume text:\n{resume_text}\n\nReturn format:\n{{\n    \"skills_analysis\": {{\n        \"technical_skills\": [],\n        \"soft_skills\": [],\n        \"tools_and_technologies\": []\n    }}\n}}\n"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(resume_text=resume_text)
        return extract_json_with_key(result, 'skills_analysis')
    
    def _extract_experience(self, resume_text: str) -> List[Dict]:
        """Extract work experience from resume text."""
        prompt = ChatPromptTemplate.from_template(
            """Extract work experience from the following resume text.\nReturn ONLY valid JSON, using double quotes for all keys and string values, and do not use triple quotes or multiline strings. Do not include markdown or explanations.\nThe JSON object MUST be wrapped in an 'experience_analysis' key as shown below.\n\nResume text:\n{resume_text}\n\nReturn format:\n{{\n    \"experience_analysis\": [\n        {{\n            \"company\": \"\",\n            \"title\": \"\",\n            \"dates\": \"\",\n            \"responsibilities\": []\n        }}\n    ]\n}}\n"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(resume_text=resume_text)
        return extract_json_with_key(result, 'experience_analysis')
    
    def _analyze_job_requirements(self, job_description: str) -> Dict:
        """Analyze job requirements from job description."""
        prompt = ChatPromptTemplate.from_template(
            """Analyze the following job description and extract key requirements.\nReturn ONLY valid JSON, using double quotes for all keys and string values, and do not use triple quotes or multiline strings. Do not include markdown or explanations.\nThe JSON object MUST be wrapped in a 'job_requirements' key as shown below.\n\nJob description:\n{job_description}\n\nReturn format:\n{{\n    \"job_requirements\": {{\n        \"required_skills\": [],\n        \"preferred_skills\": [],\n        \"responsibilities\": [],\n        \"qualifications\": []\n    }}\n}}\n"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(job_description=job_description)
        return extract_json_with_key(result, 'job_requirements')
    
    def _generate_tailored_bullets(self, resume_text: str, job_description: str) -> List[str]:
        """Generate tailored bullet points for resume."""
        prompt = ChatPromptTemplate.from_template(
            """Generate tailored bullet points for the resume based on the job description.\nReturn ONLY valid JSON, using double quotes for all keys and string values, and do not use triple quotes or multiline strings. Do not include markdown or explanations.\nThe JSON object MUST be wrapped in a 'tailored_bullets' key as shown below.\n\nResume text:\n{resume_text}\n\nJob description:\n{job_description}\n\nReturn format:\n{{\n    \"tailored_bullets\": [\n        \"Bullet point 1\",\n        \"Bullet point 2\",\n        ...\n    ]\n}}\n"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(resume_text=resume_text, job_description=job_description)
        return extract_json_with_key(result, 'tailored_bullets')
    
    def _calculate_fit_score(self, resume_text: str, job_description: str) -> Dict:
        """Calculate fit score between resume and job."""
        prompt = ChatPromptTemplate.from_template(
            """Calculate a fit score between the resume and job description.\nReturn ONLY valid JSON, using double quotes for all keys and string values, and do not use triple quotes or multiline strings. Do not include markdown or explanations.\nThe JSON object MUST be wrapped in a 'fit_analysis' key as shown below.\n\nResume text:\n{resume_text}\n\nJob description:\n{job_description}\n\nReturn format:\n{{\n    \"fit_analysis\": {{\n        \"overall_score\": 0-100,\n        \"skills_match\": 0-100,\n        \"experience_match\": 0-100,\n        \"missing_requirements\": [],\n        \"strengths\": [],\n        \"areas_for_improvement\": []\n    }}\n}}\n"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(resume_text=resume_text, job_description=job_description)
        return extract_json_with_key(result, 'fit_analysis')
    
    def _refine_analysis(self, analysis_results: Dict, job_description: str) -> Dict:
        """Refine the analysis results for better accuracy and relevance."""
        prompt = ChatPromptTemplate.from_template(
            """Refine the following resume analysis results to better match the job description.\nReturn ONLY valid JSON, using double quotes for all keys and string values, and do not use triple quotes or multiline strings. Do not include markdown or explanations.\nThe JSON object MUST be wrapped in the keys as shown below.\n\nAnalysis results:\n{analysis_results}\n\nJob description:\n{job_description}\n\nReturn format:\n{{\n    \"skills_analysis\": {{\n        \"technical_skills\": [],\n        \"soft_skills\": [],\n        \"tools_and_technologies\": []\n    }},\n    \"experience_analysis\": [\n        {{\n            \"company\": \"\",\n            \"title\": \"\",\n            \"dates\": \"\",\n            \"responsibilities\": []\n        }}\n    ],\n    \"job_requirements\": {{\n        \"required_skills\": [],\n        \"preferred_skills\": [],\n        \"responsibilities\": [],\n        \"qualifications\": []\n    }},\n    \"tailored_bullets\": [],\n    \"fit_analysis\": {{\n        \"overall_score\": 0-100,\n        \"skills_match\": 0-100,\n        \"experience_match\": 0-100,\n        \"missing_requirements\": [],\n        \"strengths\": [],\n        \"areas_for_improvement\": []\n    }}\n}}\n"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(analysis_results=str(analysis_results), job_description=job_description)
        return extract_json_with_key(result, 'skills_analysis')
    
    def analyze_resume(self, resume_text: str, job_description: str) -> Dict:
        """Perform comprehensive resume analysis and refinement."""
        # Initial analysis
        skills = self._extract_skills(resume_text)
        experience = self._extract_experience(resume_text)
        requirements = self._analyze_job_requirements(job_description)
        tailored_bullets = self._generate_tailored_bullets(resume_text, job_description)
        fit_score = self._calculate_fit_score(resume_text, job_description)
        
        # Combine results
        initial_analysis = {
            "skills_analysis": skills.get("skills_analysis", {}),
            "experience_analysis": experience.get("experience_analysis", []),
            "job_requirements": requirements.get("job_requirements", {}),
            "tailored_bullets": tailored_bullets.get("tailored_bullets", []),
            "fit_analysis": fit_score.get("fit_analysis", {})
        }
        
        # Refine results
        refined_analysis = self._refine_analysis(initial_analysis, job_description)
        
        return refined_analysis 