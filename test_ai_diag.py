import os
import sys

# Virtual env dagi kutubxonalarni tekshirish
try:
    import google.generativeai as genai
    print("SUCCESS: google-generativeai o'rnatilgan.")
except ImportError:
    print("ERROR: google-generativeai o'rnatilmagan!")

# API Key ni tekshirish
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    # Oxirgi 4 ta belgini ko'rsatamiz xavfsizlik uchun
    print(f"SUCCESS: API KEY topildi (****{api_key[-4:]})")
else:
    # .env faylini qo'lda o'qib ko'ramiz
    from pathlib import Path
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parent
    load_dotenv(BASE_DIR / '.env')
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"SUCCESS: API KEY .env dan topildi (****{api_key[-4:]})")
    else:
        print("ERROR: API KEY topilmadi!")
