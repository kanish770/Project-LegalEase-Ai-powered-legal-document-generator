import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiDocumentGenerator:
    def _init_(self, model_name: str = "gemini-1.5-pro"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set in .env file.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        prompt = (
            f"Generate a comprehensive, formal legal document titled '{document_type}'.\n\n"
            f"Involved Parties: {parties}\n"
            f"Effective Date: {dates}\n"
            f"Terms and Conditions: {terms}\n\n"
            f"Ensure formal legal structure with clear sections, titles, and legal clauses. "
            f"Do not include meta-commentary or introduction text, only output the contract itself."
        )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text