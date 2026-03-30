from core.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def get_by_email(self, email):
        return self.get_one(email=email)

    def get_by_id(self, pk):
        return self.get_one(id=pk)

    def list_users(self, limit=100, offset=0):
        return self.model.objects.all()[offset: offset + limit]

    def create_user(self, *, email, password, **extra_fields):
        """Parolni to'g'ri hash qilib user yaratadi."""
        return self.model.objects.create_user(email=email, password=password, **extra_fields)


class SpecialtyRepository(BaseRepository):
    def get_by_name(self, name):
        return self.get_one(name=name)


class ProfileRepository(BaseRepository):
    def get_by_user(self, user):
        return self.get_one(user=user)
