import os
import google.generativeai as genai
from django.conf import settings
from .models import Session, SimulationMessage

class GeminiSimulationService:
    """
    Gemini AI orqali bemor bilan muloqot va tahlil xizmati.
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY topilmadi!")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def _build_system_instruction(self, session: Session) -> str:
        """
        Bemor ssenariysi asosida AI uchun tizim ko'rsatmasini (System Prompt) tayyorlaydi.
        """
        scenario = session.scenario
        patient = scenario.patient
        
        instruction = f"""
{scenario.system_prompt}

PATIENT PROFILE:
Name: {patient.name}
Age: {patient.age}
Gender: {patient.get_gender_display()}
Chief Complaint: {patient.complaint}
Medical History: {patient.history}

INSTRUCTIONS:
1. You are the patient described above. 
2. Use natural, conversational English suitable for a patient.
3. Do not give medical diagnoses. Only answer the doctor's questions based on your symptoms and history.
4. Be concise but realistic.
5. If the doctor asks something not in your history, you can simulate a realistic response consistent with your profile.
6. Communication should be in English only.
"""
        return instruction

    def get_initial_greeting(self, session: Session) -> str:
        """
        Simulyatsiya boshida bemorning birinchi xabarini generatsiya qiladi.
        """
        system_instruction = self._build_system_instruction(session)
        prompt = "Introduce yourself briefly and state your main complaint. Start the conversation."
        
        chat = self.model.start_chat(history=[])
        response = chat.send_message(f"{system_instruction}\n\n{prompt}")
        return response.text

    def get_patient_response(self, session: Session, user_message: str) -> str:
        """
        Doktorning xabariga asosan bemor javobini generatsiya qiladi.
        """
        system_instruction = self._build_system_instruction(session)
        
        # Tarixni tayyorlaymiz
        messages = session.messages.all().order_by('timestamp')
        history = []
        for msg in messages:
            role = "user" if msg.sender == SimulationMessage.Sender.USER else "model"
            history.append({"role": role, "parts": [msg.text]})
        
        # Oxirgi xabarni olib tashlaymiz, chunki uni send_message bilan yuboramiz
        if history and history[-1]["role"] == "user":
            history.pop()

        chat = self.model.start_chat(history=history)
        
        # Tizim instruktsiyasini birinchi xabar sifatida (yoki context sifatida) berish mumkin.
        # Lekin Gemini 1.5 da system_instruction parametri bor.
        
        model_with_instruction = genai.GenerativeModel(
            model_name='gemini-flash-latest',
            system_instruction=system_instruction
        )
        chat = model_with_instruction.start_chat(history=history)
        
        response = chat.send_message(user_message)
        return response.text

    def evaluate_session(self, session: Session) -> str:
        """
        Sessiya yakunida talabaning bilimini baholash va feedback berish.
        """
        messages = session.messages.all().order_by('timestamp')
        conversation_text = ""
        for msg in messages:
            sender_name = "Doctor" if msg.sender == SimulationMessage.Sender.USER else "Patient"
            conversation_text += f"{sender_name}: {msg.text}\n"

        prompt = f"""
As a medical instructor, evaluate the following conversation between a medical student (Doctor) and a virtual patient.
Scenario: {session.scenario.title}
Patient: {session.scenario.patient.name}

Conversation:
{conversation_text}

Provide your evaluation in a clear format. 
1. SCORE: (0-100)
2. FEEDBACK_EN: (Overall feedback in English)
3. FEEDBACK_UZ: (Overall feedback in Uzbek)
4. STRENGTHS: (List of points)
5. AREAS FOR IMPROVEMENT: (List of points)

Be professional and constructive.
"""
        response = self.model.generate_content(prompt)
        return response.text
