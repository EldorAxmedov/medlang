from django.db import transaction

from chat.models import ChatRoom, ChatParticipant, ChatMessage
from chat.repositories import (
    ChatRoomRepository,
    ChatParticipantRepository,
    ChatMessageRepository,
)


# ─── Singleton repositories ─────────────────────────────────────

def _room_repo() -> ChatRoomRepository:
    return ChatRoomRepository(ChatRoom)


def _participant_repo() -> ChatParticipantRepository:
    return ChatParticipantRepository(ChatParticipant)


def _message_repo() -> ChatMessageRepository:
    return ChatMessageRepository(ChatMessage)


# ─── ChatService ────────────────────────────────────────────────

class ChatService:
    """
    Chat tizimi biznes mantiq.
    Xabarlar yuborish, guruhlar yaratish va tarixlarni boshqaradi.
    """

    def __init__(
        self,
        room_repo: ChatRoomRepository = None,
        participant_repo: ChatParticipantRepository = None,
        message_repo: ChatMessageRepository = None,
    ):
        self.room_repo = room_repo or _room_repo()
        self.participant_repo = participant_repo or _participant_repo()
        self.message_repo = message_repo or _message_repo()

    # ── Room yaratish ──────────────────────────────────────────

    @transaction.atomic
    def create_group(self, creator_user, name: str, member_ids: list = None) -> ChatRoom:
        """
        Yangi guruh yaraydi va creator'ni admin qiladi.
        """
        room = self.room_repo.create(name=name, type=ChatRoom.RoomType.GROUP)
        
        # Creator ni qo'shish
        self.participant_repo.create(
            user=creator_user,
            chat_room=room,
            role=ChatParticipant.Role.ADMIN
        )

        # Boshqa a'zolarni qo'shish
        if member_ids:
            for uid in member_ids:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=uid)
                self.participant_repo.create(user=user, chat_room=room)
        
        return room

    @transaction.atomic
    def get_or_create_private_chat(self, user1, user2_id: str) -> ChatRoom:
        """
        Ikki kishilik chatni topadi yoki yangi yaratadi.
        """
        if str(user1.id) == str(user2_id):
            # O'zi bilan o'zi gaplashish holatini boshqarish yoki taqiqlash
            # Bu yerda shunchaki mavjud xonani qidirib ko'ramiz
            pass

        existing = self.participant_repo.find_private_room(user1.id, user2_id)
        if existing:
            return existing

        # Yaratish
        room = self.room_repo.create(type=ChatRoom.RoomType.PRIVATE)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user2 = User.objects.get(id=user2_id)

        # Qatnashchilarni qo'shish (bir xil user bitta chatda 2 marta bo'la olmaydi)
        self.participant_repo.create(user=user1, chat_room=room)
        
        if str(user1.id) != str(user2_id):
            self.participant_repo.create(user=user2, chat_room=room)
        
        return room

    # ── Muloqot ────────────────────────────────────────────────

    @transaction.atomic
    def send_message(self, sender, room_id: str, text: str) -> ChatMessage:
        """
        Xabar yozish.
        """
        room = self.room_repo.get_one(pk=room_id)
        if not room:
            raise ValueError("Chat xonasi topilmadi.")

        msg = self.message_repo.create(
            chat_room=room,
            sender=sender,
            text=text
        )
        return msg

    def list_history(self, room_id, limit: int = 50, offset: int = 0):
        return self.message_repo.list_for_room(room_id, limit=limit, offset=offset)

    def list_user_rooms(self, user_id):
        return self.room_repo.list_rooms_for_user(user_id)

    @transaction.atomic
    def read_all_messages(self, room_id, user_id):
        return self.message_repo.mark_as_read(room_id, user_id)
