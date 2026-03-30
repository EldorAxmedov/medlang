from django.contrib import admin
from .models import User, Profile, Specialty


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'role', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name')
    list_filter = ('role', 'is_staff', 'is_active')


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty')
    search_fields = ('user__email', 'user__full_name')
    raw_id_fields = ('user',)
