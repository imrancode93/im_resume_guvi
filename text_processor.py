import re
from typing import List, Dict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class TextProcessor:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """Extract keywords from text."""
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Tokenize
        tokens = word_tokenize(cleaned_text)
        
        # Remove stopwords and short words
        keywords = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and len(token) >= min_length
        ]
        
        return list(set(keywords))
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using Jaccard similarity."""
        # Extract keywords from both texts
        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))
        
        # Calculate Jaccard similarity
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        
        return intersection / union if union > 0 else 0.0
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from text and categorize them."""
        # Common skill categories and their keywords
        categories = {
            "technical_skills": [
                "programming", "software", "database", "framework",
                "language", "tool", "technology", "system"
            ],
            "soft_skills": [
                "communication", "leadership", "teamwork", "problem-solving",
                "time management", "adaptability", "creativity"
            ],
            "tools_and_technologies": [
                "software", "platform", "application", "system",
                "tool", "technology", "framework"
            ]
        }
        
        # Extract keywords
        keywords = self.extract_keywords(text)
        
        # Categorize skills
        categorized_skills = {
            category: []
            for category in categories.keys()
        }
        
        for keyword in keywords:
            for category, indicators in categories.items():
                if any(indicator in keyword for indicator in indicators):
                    categorized_skills[category].append(keyword)
        
        return categorized_skills
    
    def format_bullet_points(self, text: str) -> List[str]:
        """Format text into bullet points."""
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and format each sentence
        bullet_points = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Ensure sentence starts with a capital letter
                sentence = sentence[0].upper() + sentence[1:]
                bullet_points.append(sentence)
        
        return bullet_points
    
    def optimize_for_ats(self, text: str, keywords: List[str]) -> str:
        """Optimize text for ATS systems."""
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Ensure keywords are present
        for keyword in keywords:
            if keyword.lower() not in cleaned_text.lower():
                # Add keyword in a natural way if missing
                sentences = cleaned_text.split('.')
                if sentences:
                    # Add to the first sentence
                    sentences[0] = f"{sentences[0]} {keyword}."
                    cleaned_text = '. '.join(sentences)
        
        return cleaned_text 