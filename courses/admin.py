from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import InteractiveExercise, UserExerciseAttempt

from .models import CodeExample, Course, Lesson, Module, Technology, WorkflowDiagram


class CodeExampleInline(admin.TabularInline):
    model = CodeExample
    extra = 1
    fields = ['title', 'language', 'order']
    ordering = ['order']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 4, 'cols': 40})},
    }

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'lesson_type', 'order', 'is_free']
    ordering = ['order']

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ['title', 'order']
    ordering = ['order']

class LessonAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = '__all__'
        widgets = {
            'content': CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
        }

class CodeExampleAdminForm(forms.ModelForm):
    class Meta:
        model = CodeExample
        fields = '__all__'
        widgets = {
            'explanation': CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="default"
            ),
        }

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'phase', 'order', 'official_docs_link']
    list_filter = ['category', 'phase']
    ordering = ['phase', 'order']
    search_fields = ['name', 'description']
    
    def official_docs_link(self, obj):
        if obj.official_docs_url:
            return format_html('<a href="{}" target="_blank">📚 Docs</a>', obj.official_docs_url)
        return "-"
    official_docs_link.short_description = "Official Docs"

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'technology', 'difficulty', 'estimated_duration', 'lesson_count', 'is_active']
    list_filter = ['difficulty', 'is_active', 'technology__phase']
    search_fields = ['title', 'description']
    inlines = [ModuleInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('technology', 'title', 'description', 'difficulty')
        }),
        ('Metadata', {
            'fields': ('estimated_duration', 'prerequisites', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def lesson_count(self, obj):
        return obj.lessons_count()
    lesson_count.short_description = 'Lessons'

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'lesson_count']
    list_filter = ['course']
    ordering = ['course', 'order']
    inlines = [LessonInline]
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Lessons'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    list_display = ['title', 'module', 'lesson_type', 'order', 'duration_minutes', 'is_free', 'created_at']
    list_filter = ['lesson_type', 'is_free', 'module__course']
    ordering = ['module', 'order']
    search_fields = ['title', 'content']
    inlines = [CodeExampleInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('module', 'title', 'content', 'lesson_type')
        }),
        ('Media & Resources', {
            'fields': ('video_url',)
        }),
        ('Settings', {
            'fields': ('order', 'duration_minutes', 'is_free')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        css = {
            'all': ('django_ckeditor_5/admin.css',)
        }

@admin.register(WorkflowDiagram)
class WorkflowDiagramAdmin(admin.ModelAdmin):
    list_display = ['title', 'technology', 'order']
    list_filter = ['technology']
    ordering = ['technology', 'order']
    list_editable = ['order']

@admin.register(CodeExample)
class CodeExampleAdmin(admin.ModelAdmin):
    form = CodeExampleAdminForm
    list_display = ['title', 'lesson', 'language', 'order']
    list_filter = ['language', 'lesson__module__course']
    ordering = ['lesson', 'order']
    list_editable = ['order']
    
    class Media:
        css = {
            'all': ('django_ckeditor_5/admin.css',)
        }
        
@admin.register(InteractiveExercise)
class InteractiveExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'exercise_type', 'points', 'order', 'get_total_attempts', 'get_success_rate']
    list_filter = ['exercise_type', 'lesson__module__course']
    ordering = ['lesson', 'order']
    search_fields = ['title', 'instructions']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('lesson', 'title', 'exercise_type', 'instructions')
        }),
        ('Code Exercise Settings', {
            'fields': ('initial_code', 'solution_code', 'test_cases'),
            'classes': ('collapse',)
        }),
        ('Quiz Exercise Settings', {
            'fields': ('options',),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('points', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_attempts(self, obj):
        return obj.get_total_attempts()
    get_total_attempts.short_description = 'Total Attempts'
    
    def get_success_rate(self, obj):
        return f"{obj.get_success_rate():.1f}%"
    get_success_rate.short_description = 'Success Rate'

@admin.register(UserExerciseAttempt)
class UserExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'is_correct', 'score', 'attempted_at', 'completed_at']
    list_filter = ['is_correct', 'exercise__lesson__module__course', 'attempted_at']
    ordering = ['-attempted_at']
    search_fields = ['user__username', 'exercise__title']
    readonly_fields = ['attempted_at', 'completed_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'exercise')
        }),
        ('Submission Details', {
            'fields': ('code_submission', 'answers')
        }),
        ('Results', {
            'fields': ('is_correct', 'score')
        }),
        ('Timestamps', {
            'fields': ('attempted_at', 'completed_at')
        }),
    )