from typing import Generic, TypeVar

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository - minimal abstraction for DB operations.

    Concrete repositories should receive Django model classes via DI.
    """

    def __init__(self, model):
        self.model = model

    def get(self, **filters):
        return self.model.objects.filter(**filters)

    def get_one(self, **filters):
        return self.model.objects.filter(**filters).first()

    def create(self, **data):
        return self.model.objects.create(**data)

    def update(self, instance, **data):
        for k, v in data.items():
            setattr(instance, k, v)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()
