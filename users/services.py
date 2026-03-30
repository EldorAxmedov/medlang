from django.contrib.auth import authenticate


class UserService:
    def __init__(self, repository, password_hasher=None):
        self.repository = repository
        self.password_hasher = password_hasher

    def register(self, *, email, password, full_name=None, role=None):
        existing = self.repository.get_by_email(email)
        if existing:
            raise ValueError('email_already_exists')
        data = {
            'email': email,
            'full_name': full_name or '',
            'role': role or 'user',
        }
        user = self.repository.create_user(**data, password=password)
        return user

    def authenticate_user(self, email: str, password: str):
        user = authenticate(username=email, password=password)
        return user

    def get_user(self, user_id):
        return self.repository.get_by_id(user_id)


class SpecialtyService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, name: str, description: str = ''):
        existing = self.repository.get_by_name(name)
        if existing:
            return existing
        return self.repository.create(name=name, description=description)

    def get(self, name: str):
        return self.repository.get_by_name(name)


class ProfileService:
    def __init__(self, repository, user_repository=None):
        self.repository = repository
        self.user_repository = user_repository

    def create_or_update(self, user, *, specialty=None, bio=None, avatar=None):
        profile = self.repository.get_by_user(user)
        data = {}
        if specialty is not None:
            data['specialty'] = specialty
        if bio is not None:
            data['bio'] = bio
        if avatar is not None:
            data['avatar'] = avatar

        if profile:
            return self.repository.update(profile, **data)
        payload = {'user': user}
        payload.update(data)
        return self.repository.create(**payload)
