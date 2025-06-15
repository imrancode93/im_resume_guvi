from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import Dict
import re
import json5

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

class CoverLetterAgent:
    """Agent for generating and optimizing cover letters using an LLM."""
    def __init__(self, llm):
        """Initialize with a language model."""
        self.llm = llm
        self.tools = self._create_tools()
    
    def _create_tools(self) -> list[Tool]:
        """Create tools for cover letter generation and optimization."""
        return [
            Tool(
                name="generate_cover_letter",
                func=self._generate_cover_letter,
                description="Generates a personalized cover letter"
            ),
            Tool(
                name="optimize_cover_letter",
                func=self._optimize_cover_letter,
                description="Optimizes the cover letter for ATS and readability"
            ),
            Tool(
                name="refine_tone",
                func=self._refine_tone,
                description="Refines the tone and style of the cover letter"
            ),
            Tool(
                name="enhance_impact",
                func=self._enhance_impact,
                description="Enhances the impact of key achievements and qualifications"
            )
        ]
    
    def _generate_cover_letter(self, resume_text: str, job_description: str) -> Dict:
        """Generate a personalized cover letter."""
        prompt = ChatPromptTemplate.from_template(
            """Generate a professional cover letter based on the resume and job description.
            The cover letter should be personalized, highlight relevant experience,
            and demonstrate enthusiasm for the position.
            Return ONLY the following JSON object, with no explanation, markdown, or extra text.
            
            Resume text:
            {resume_text}
            
            Job description:
            {job_description}
            
            Return format:
            {{
                "cover_letter": "Full cover letter text",
                "key_points": [
                    "Key point 1",
                    "Key point 2",
                    ...
                ],
                "tone": "Professional and enthusiastic",
                "length": "Number of words"
            }}
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(resume_text=resume_text, job_description=job_description)
        return extract_json_with_key(result, 'cover_letter')
    
    def _optimize_cover_letter(self, cover_letter: str, job_description: str) -> Dict:
        """Optimize the cover letter for ATS and readability."""
        prompt = ChatPromptTemplate.from_template(
            """Optimize the following cover letter for ATS systems and readability.
            Ensure it includes relevant keywords from the job description while maintaining
            a natural flow and professional tone.
            Return ONLY the following JSON object, with no explanation, markdown, or extra text.
            
            Cover letter:
            {cover_letter}
            
            Job description:
            {job_description}
            
            Return format:
            {{
                "optimized_letter": "Optimized cover letter text",
                "keywords_used": [
                    "Keyword 1",
                    "Keyword 2",
                    ...
                ],
                "readability_score": "Score out of 100",
                "improvements_made": [
                    "Improvement 1",
                    "Improvement 2",
                    ...
                ]
            }}
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(cover_letter=cover_letter, job_description=job_description)
        return extract_json_with_key(result, 'cover_letter')
    
    def _refine_tone(self, cover_letter: str, job_description: str) -> Dict:
        """Refine the tone and style of the cover letter."""
        prompt = ChatPromptTemplate.from_template(
            """Refine the tone and style of the following cover letter to better match the company culture
            and job requirements. Make it more engaging and professional while maintaining authenticity.
            Return ONLY the following JSON object, with no explanation, markdown, or extra text.
            
            Cover letter:
            {cover_letter}
            
            Job description:
            {job_description}
            
            Return format:
            {{
                "refined_letter": "Refined cover letter text",
                "tone_analysis": {{
                    "formality_level": "Formal/Semi-formal/Casual",
                    "enthusiasm_level": "High/Medium/Low",
                    "confidence_level": "High/Medium/Low"
                }},
                "style_improvements": [
                    "Improvement 1",
                    "Improvement 2",
                    ...
                ]
            }}
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(cover_letter=cover_letter, job_description=job_description)
        return extract_json_with_key(result, 'cover_letter')
    
    def _enhance_impact(self, cover_letter: str, resume_text: str) -> Dict:
        """Enhance the impact of key achievements and qualifications."""
        prompt = ChatPromptTemplate.from_template(
            """Enhance the impact of key achievements and qualifications in the cover letter
            by making them more specific, measurable, and relevant to the position.
            Return ONLY the following JSON object, with no explanation, markdown, or extra text.
            
            Cover letter:
            {cover_letter}
            
            Resume:
            {resume_text}
            
            Return format:
            {{
                "enhanced_letter": "Enhanced cover letter text",
                "key_achievements": [
                    {{
                        "achievement": "",
                        "impact": "",
                        "relevance": ""
                    }}
                ],
                "improvements_made": [
                    "Improvement 1",
                    "Improvement 2",
                    ...
                ]
            }}
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(cover_letter=cover_letter, resume_text=resume_text)
        return extract_json_with_key(result, 'cover_letter')
    
    def generate_optimized_cover_letter(self, resume_text: str, job_description: str) -> Dict:
        """Generate and optimize a cover letter through multiple refinement steps."""
        # Generate initial cover letter
        initial_letter = self._generate_cover_letter(resume_text, job_description)
        
        # Optimize for ATS
        optimized = self._optimize_cover_letter(initial_letter["cover_letter"], job_description)
        
        # Refine tone
        tone_refined = self._refine_tone(optimized["optimized_letter"], job_description)
        
        # Enhance impact
        final_letter = self._enhance_impact(tone_refined["refined_letter"], resume_text)
        
        return {
            "initial_cover_letter": initial_letter,
            "ats_optimized": optimized,
            "tone_refined": tone_refined,
            "final_letter": final_letter["enhanced_letter"],
            "analysis": {
                "tone_analysis": tone_refined["tone_analysis"],
                "key_achievements": final_letter["key_achievements"],
                "improvements": {
                    "ats": optimized["improvements_made"],
                    "tone": tone_refined["style_improvements"],
                    "impact": final_letter["improvements_made"]
                }
            }
        } 