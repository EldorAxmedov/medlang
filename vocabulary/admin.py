from django.contrib import admin
from .models import Category, Word, Translation, Definition, Example


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 1


class DefinitionInline(admin.TabularInline):
    model = Definition
    extra = 1


class ExampleInline(admin.TabularInline):
    model = Example
    extra = 1


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('term', 'difficulty', 'created_at')
    search_fields = ('term',)
    list_filter = ('difficulty', 'categories')
    inlines = (TranslationInline, DefinitionInline, ExampleInline)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
