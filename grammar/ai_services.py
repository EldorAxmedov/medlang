import os
import json
import google.generativeai as genai
from django.conf import settings

class GeminiGrammarService:
    """
    Gemini AI orqali tibbiy matnlarni grammatik va stilistik tahlil qilish xizmati.
    """

    def __init__(self):
        # API Key ni yuklash
        from pathlib import Path
        from dotenv import load_dotenv
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        load_dotenv(BASE_DIR / '.env')

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY topilmadi!")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_text(self, text: str) -> dict:
        """
        Matnni tahlil qiladi va JSON formatida natija qaytaradi.
        """
        prompt = f"""
As a professional medical English editor, analyze the following medical text for grammar, spelling, and medical stylistic errors.
Provide a corrected version and a detailed list of errors found.

TEXT TO ANALYZE:
"{text}"

RESPONSE FORMAT (JSON ONLY):
{{
    "corrected_text": "The full corrected version of the text",
    "score": 85,
    "errors": [
        {{
            "original": "bad word",
            "suggestion": "better word",
            "type": "grammar/spelling/style",
            "explanation": "Why it was wrong"
        }}
    ],
    "overall_feedback": "General advice for improvement"
}}

Ensure the JSON is valid and only includes the requested fields.
"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            # JSON-ni tozalash (ba'zan AI ```json ichida qaytaradi)
            content = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        except Exception as e:
            # Xatolikni logga yozish
            import traceback
            traceback.print_exc()
            return {
                "corrected_text": text,
                "score": 0,
                "errors": [],
                "overall_feedback": f"Error: {str(e)}"
            }
