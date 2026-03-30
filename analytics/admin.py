from django.contrib import admin
from analytics.models import ActivityLog, DailyStatistic


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'module', 'action', 'timestamp')
    search_fields = ('user__email', 'module', 'action')
    list_filter = ('module', 'action', 'timestamp')
    readonly_fields = ('user', 'module', 'action', 'data', 'timestamp')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'

    # Activity logni o'lda o'zgartirib bo'lmaydi
    def has_add_permission(self, request):
        return False


@admin.register(DailyStatistic)
class DailyStatisticAdmin(admin.ModelAdmin):
    list_display = ('date', 'active_users', 'tests_taken', 'simulations_started', 'messages_sent')
    search_fields = ('date',)
    list_filter = ('date',)
    readonly_fields = ('active_users', 'tests_taken', 'simulations_started', 'messages_sent', 'date')

    # Faqat ko'rish mumkin
    def has_add_permission(self, request):
        return False
