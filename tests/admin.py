from django.contrib import admin
from tests.models import Test, Question, Answer, UserResult


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    fields = ('text', 'is_correct')


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True # Bu savolni alohida tahrirlashga link beradi


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('difficulty', 'category', 'created_at')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'text_snippet', 'created_at')
    search_fields = ('text', 'test__title')
    list_filter = ('test__category', 'test')
    inlines = [AnswerInline]

    def text_snippet(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
    text_snippet.short_description = 'Savol matni'


@admin.register(UserResult)
class UserResultAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'test_title', 'score', 'correct_answers', 'total_questions', 'completed_at')
    search_fields = ('user__email', 'test__title')
    list_filter = ('test', 'completed_at')
    readonly_fields = ('user', 'test', 'score', 'total_questions', 'correct_answers', 'completed_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'

    def test_title(self, obj):
        return obj.test.title
    test_title.short_description = 'Test'
    
    # UserResult ni o'zgartirib bo'lmaydi (Faqat ko'rish mumkin)
    def has_add_permission(self, request):
        return False
