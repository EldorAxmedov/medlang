from django.contrib import admin
from grammar.models import GrammarCheck


@admin.register(GrammarCheck)
class GrammarCheckAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'score', 'created_at')
    search_fields = ('user__email', 'original_text')
    list_filter = ('score', 'created_at')
    readonly_fields = ('user', 'original_text', 'corrected_text', 'error_details', 'score', 'created_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'

    # Grammar check natijasini qo'lda o'zgartirib bo'lmaydi
    def has_add_permission(self, request):
        return False
