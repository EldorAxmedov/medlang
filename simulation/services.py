from django.db import transaction

from .models import Scenario, PatientProfile, Session, SimulationMessage
from .repositories import (
    ScenarioRepository,
    PatientProfileRepository,
    SessionRepository,
    SimulationMessageRepository,
)
from .ai_services import GeminiSimulationService


# ─── Singleton repositories ─────────────────────────────────────

def _scenario_repo() -> ScenarioRepository:
    return ScenarioRepository(Scenario)


def _patient_repo() -> PatientProfileRepository:
    return PatientProfileRepository(PatientProfile)


def _session_repo() -> SessionRepository:
    return SessionRepository(Session)


def _message_repo() -> SimulationMessageRepository:
    return SimulationMessageRepository(SimulationMessage)


# ─── SimulationService ──────────────────────────────────────────

class SimulationService:
    """
    Simulyatsiya biznes mantiq.
    Talaba bilan virtual bemor orasidagi muloqotni boshqaradi.
    """

    def __init__(
        self,
        scenario_repo: ScenarioRepository = None,
        patient_repo: PatientProfileRepository = None,
        session_repo: SessionRepository = None,
        message_repo: SimulationMessageRepository = None,
        ai_service: GeminiSimulationService = None,
    ):
        self.scenario_repo = scenario_repo or _scenario_repo()
        self.patient_repo = patient_repo or _patient_repo()
        self.session_repo = session_repo or _session_repo()
        self.message_repo = message_repo or _message_repo()
        self.ai_service = ai_service or GeminiSimulationService()

    # ── Sessiya boshlash ────────────────────────────────────────

    @transaction.atomic
    def start_session(self, user, scenario_id: str) -> Session:
        """
        Yangi simulyatsiya sessiyasini boshlaydi.
        Ssenariy va unga tegishli bemor ma'lumotlarini tekshiradi.
        """
        scenario = self.scenario_repo.get_one(pk=scenario_id)
        if not scenario:
            raise ValueError(f"Ssenariy topilmadi: '{scenario_id}'")

        # Mavjud aktiv sessiyani qidirish (agar kerak bo'lsa)
        # Hozircha cheklovsiz har safar yangi yaratadi
        
        session = self.session_repo.create(
            user=user,
            scenario=scenario,
            status=Session.Status.ACTIVE
        )

        # Gemini dan birinchi greetingni olish
        greeting = self.ai_service.get_initial_greeting(session)
        self.save_patient_message(session.id, greeting)

        return session

    # ── Muloqotni boshqarish ─────────────────────────────────────

    @transaction.atomic
    def send_user_message(self, session_id: str, text: str) -> tuple[SimulationMessage, SimulationMessage]:
        """
        Doktor/Talaba xabarini saqlaydi va AI orqali bemor javobini oladi.
        """
        session = self.session_repo.get_one(pk=session_id)
        if not session or session.status != Session.Status.ACTIVE:
            raise ValueError("Aktiv sessiya topilmadi.")

        # 1. Foydalanuvchi xabari
        user_msg = self.message_repo.create(
            session=session,
            sender=SimulationMessage.Sender.USER,
            text=text
        )

        # 2. Gemini orqali bemor javobi
        patient_reply_text = self.ai_service.get_patient_response(session, text)
        patient_msg = self.save_patient_message(session.id, patient_reply_text)

        return user_msg, patient_msg

    @transaction.atomic
    def save_patient_message(self, session_id: str, text: str) -> SimulationMessage:
        """
        Bemor/AI xabarini tizim nomidan saqlaydi.
        """
        session = self.session_repo.get_one(pk=session_id)
        if not session:
            raise ValueError("Sessiya topilmadi.")

        return self.message_repo.create(
            session=session,
            sender=SimulationMessage.Sender.PATIENT,
            text=text
        )

    # ── Yakunlash va Feedback ───────────────────────────────────

    @transaction.atomic
    def complete_session(self, session_id: str, score: int, feedback: str) -> Session:
        """
        Sessiyani yopish va ball berish.
        Bu API orqali AI tahlili natijasida olingan ma'lumot bo'lishi mumkin.
        """
        session = self.session_repo.get_one(pk=session_id)
        if not session:
            raise ValueError("Sessiya topilmadi.")

        return self.session_repo.update(
            session,
            status=Session.Status.COMPLETED,
            score=max(0, min(100, score)),
            feedback=feedback
        )

    # ── Ma'lumotlarni ko'rish ───────────────────────────────────

    def get_full_history(self, session_id: str):
        session = self.session_repo.get_with_messages(session_id)
        if not session:
            raise ValueError("Sessiya topilmadi.")
        return session

    def list_user_simulations(self, user_id, limit: int = 15):
        return self.session_repo.list_for_user(user_id, limit=limit)
