from django.contrib import admin
from progress.models import Level, UserProgress


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'threshold', 'icon')
    search_fields = ('name',)
    ordering = ('threshold',)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'level', 'total_score', 'completed_tests', 'completed_sessions', 'updated_at')
    search_fields = ('user__email',)
    list_filter = ('level', 'updated_at')
    readonly_fields = ('user', 'total_score', 'completed_tests', 'completed_sessions', 'words_learned', 'updated_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'

    # Level ni alohida o'zgartirish ruxsat etiladi (admin tomonidan)
    fields = ('user', 'level', 'total_score', 'completed_tests', 'completed_sessions', 'words_learned', 'updated_at')
