from django.contrib import admin
from simulation.models import Scenario, PatientProfile, Session, SimulationMessage


class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    verbose_name_plural = 'Patient Information'


class SimulationMessageInline(admin.TabularInline):
    model = SimulationMessage
    extra = 0
    readonly_fields = ('sender', 'text', 'timestamp')
    can_delete = False


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('title', 'specialty', 'difficulty', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('difficulty', 'specialty', 'created_at')
    inlines = [PatientProfileInline]


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'scenario_title', 'status', 'score', 'created_at')
    search_fields = ('user__email', 'scenario__title')
    list_filter = ('status', 'scenario__difficulty', 'created_at')
    readonly_fields = ('user', 'scenario', 'status', 'score', 'feedback', 'created_at')
    inlines = [SimulationMessageInline]

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'

    def scenario_title(self, obj):
        return obj.scenario.title
    scenario_title.short_description = 'Scenario'

    def difficulty_from_scenario(self, obj):
        return obj.scenario.difficulty
    difficulty_from_scenario.short_description = 'Difficulty'
    
    # Session ni o'zgartirib bo'lmaydi (Faqat ko'rish mumkin)
    def has_add_permission(self, request):
        return False


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'gender', 'scenario')
    search_fields = ('name', 'scenario__title')
    list_filter = ('gender', 'age')


@admin.register(SimulationMessage)
class SimulationMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'text_snippet', 'timestamp')
    search_fields = ('text', 'session__user__email')
    list_filter = ('sender', 'timestamp')

    def text_snippet(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
    text_snippet.short_description = 'Message'
