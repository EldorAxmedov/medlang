from core.repositories.base import BaseRepository


class ScenarioRepository(BaseRepository):
    """Scenario uchun barcha DB operatsiyalari."""

    def list_by_specialty(self, specialty_id, limit: int = 50):
        return self.model.objects.filter(specialty_id=specialty_id).order_by('difficulty')[:limit]

    def list_all(self, limit: int = 50, offset: int = 0):
        return self.model.objects.all().order_by('created_at')[offset: offset + limit]


class PatientProfileRepository(BaseRepository):
    """PatientProfile uchun barcha DB operatsiyalari."""

    def get_by_scenario(self, scenario_id):
        return self.model.objects.filter(scenario_id=scenario_id).first()


class SessionRepository(BaseRepository):
    """Session uchun barcha DB operatsiyalari."""

    def list_for_user(self, user_id, status=None, limit: int = 20):
        qs = self.model.objects.filter(user_id=user_id)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')[:limit]

    def get_with_messages(self, pk):
        return self.model.objects.prefetch_related('messages').filter(pk=pk).first()


class SimulationMessageRepository(BaseRepository):
    """SimulationMessage uchun barcha DB operatsiyalari."""

    def list_for_session(self, session_id):
        return self.model.objects.filter(session_id=session_id).order_by('timestamp')
