from django.contrib import admin
from chat.models import ChatRoom, ChatParticipant, ChatMessage


class ChatParticipantInline(admin.TabularInline):
    model = ChatParticipant
    extra = 1
    autocomplete_fields = ['user']


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('sender', 'text', 'is_read', 'created_at')
    can_delete = False


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created_at', 'participant_count')
    search_fields = ('name',)
    list_filter = ('type', 'created_at')
    inlines = [ChatParticipantInline, ChatMessageInline]

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Members'


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat_room', 'role', 'joined_at')
    search_fields = ('user__email', 'chat_room__name')
    list_filter = ('role', 'joined_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat_room', 'sender_email', 'text_snippet', 'is_read', 'created_at')
    search_fields = ('text', 'sender__email', 'chat_room__name')
    list_filter = ('is_read', 'created_at')
    readonly_fields = ('chat_room', 'sender', 'text', 'is_read', 'created_at')

    def sender_email(self, obj):
        return obj.sender.email
    sender_email.short_description = 'From'

    def text_snippet(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
    text_snippet.short_description = 'Message'
