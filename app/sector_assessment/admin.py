from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from sector_assessment.models import (Question, Choice,
                                      Assessment, QuestionAttempt,
                                      AssessmentRun, Result)
# Register your models here.


# Class to generate choice in line or one line
# if we want muliple lines we use StackedInline
class ChoiceInline(admin.StackedInline):
    model = Choice
    fields = ['choice_text', 'choice_image', 'skills']
    readonly_fields = ['created_by']
    filter_horizontal = ['skills']
    extra = 4
    ordering = ['_order']

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    ordering = ['title']
    list_display = ['title', 'id', 'created_by']
    search_fields = ['title', 'id', 'question_text']
    # Add choice creation in-line
    inlines = [ChoiceInline]
    readonly_fields = ['created_by']
    fieldsets = [
        (
            None,
            {
                'fields': ['title', 'question_text', 'question_image']
            },
        ),
    ]

    add_fieldsets = [
        (
            None,
            {
                'fields': ['title', 'question_text', 'question_image']
            },
        ),
    ]

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    ordering = ['title']
    search_fields = ['title', 'id']
    list_display = ['title', 'id', 'created_by']
    fields = ['title', 'questions', 'allowed_users']
    filter_horizontal = ['questions', 'allowed_users']
    readonly_fields = ['created_by']

    def save_model(self, request, obj, form, change):
        if not change:
            if Assessment.objects.filter(title__iexact=obj.title).count() > 0:
                raise ValidationError(
                    _("A sector with the name '%(value)s' already exists."),
                    params={'value': obj.title},
                )
        if not obj.created_by:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)


@admin.register(AssessmentRun)
class AssessmentRunAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'id', 'user']
    search_fields = ['assessment', 'id', 'user']
    readonly_fields = ('id', 'assessment', 'user', 'start_time',
                       'question_counter', 'time_taken', 'is_finished')

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False


@admin.register(QuestionAttempt)
class QuestionAttemptAdmin(admin.ModelAdmin):
    list_display = ['question', 'id', 'user']
    search_fields = ['question', 'id', 'user']
    readonly_fields = ('id', 'question', 'choice', 'user')

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['assessment_run', 'id', 'user']
    search_fields = ['assessment_run', 'id', 'user']
    readonly_fields = ('id', 'assessment_run', 'sector_score',
                       'skill_score', 'user')

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
