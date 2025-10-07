import google.generativeai as genai
import os
from typing import Optional
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    """Service class for Gemini AI integration"""
    
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Gemini model"""
        try:
            # Get API key from environment or Streamlit secrets
            api_key = os.getenv('GOOGLE_API_KEY') or st.secrets.get('GOOGLE_API_KEY')
            
            if not api_key:
                st.error("Google API key not found. Please set GOOGLE_API_KEY environment variable or add it to Streamlit secrets.")
                return
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
        except Exception as e:
            st.error(f"Failed to initialize Gemini model: {str(e)}")
            self.model = None
    
    def generate_summary(self, text: str, title: str = "") -> Optional[str]:
        """Generate summary using Gemini 2.0 Flash"""
        if not self.model:
            return None
        
        try:
            # Create a focused prompt for summarization
            prompt = f"""
            You are an expert in financial notifications and regulatory circulars. Read the following text carefully and do the following:
1. Summarize the content in a detailed and clear manner, capturing all important points.
2. Identify and list any other circulars, notifications, or references mentioned within the text.
3. If dates, numbers, or entities are mentioned, include them in the summary.
4. Present the summary in structured bullet points for easy readability.
5. Keep the language precise and professional, suitable for regulatory or financial reporting.

Title: {title}

Text to summarize:

{text}
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")
            return None
    
    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return self.model is not None
