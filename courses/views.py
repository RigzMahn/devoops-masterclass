from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView

from users.models import UserProgress

from .models import Course, Lesson, Module, Technology, WorkflowDiagram


class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        return Course.objects.filter(is_active=True).select_related('technology').prefetch_related(
            Prefetch('modules', queryset=Module.objects.annotate(lesson_count=Count('lessons')))
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group technologies by phase for navigation
        technologies_by_phase = {}
        for tech in Technology.objects.all():
            if tech.phase not in technologies_by_phase:
                technologies_by_phase[tech.phase] = []
            technologies_by_phase[tech.phase].append(tech)
        context['technologies_by_phase'] = technologies_by_phase
        return context

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_queryset(self):
        return Course.objects.filter(is_active=True).select_related('technology').prefetch_related(
            Prefetch('modules__lessons', queryset=Lesson.objects.order_by('order'))
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['technologies_in_phase'] = Technology.objects.filter(
            phase=self.object.technology.phase
        ).exclude(id=self.object.technology.id)
        
        # Add progress information if user is authenticated
        if self.request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(user=self.request.user, course=self.object)
                context['user_progress'] = progress
                context['completed_lessons'] = progress.completed_lessons.values_list('id', flat=True)
            except UserProgress.DoesNotExist:
                context['user_progress'] = None
                context['completed_lessons'] = []
        
        return context

class TechnologyDetailView(DetailView):
    model = Technology
    template_name = 'courses/technology_detail.html'
    context_object_name = 'technology'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workflows'] = WorkflowDiagram.objects.filter(technology=self.object).order_by('order')
        context['related_courses'] = Course.objects.filter(
            technology__category=self.object.category
        ).exclude(technology=self.object).select_related('technology')[:4]
        return context

class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create user progress for this course
        course = self.object.module.course
        user_progress, created = UserProgress.objects.get_or_create(
            user=self.request.user,
            course=course
        )
        
        # Update last accessed lesson
        user_progress.last_accessed_lesson = self.object
        user_progress.save()
        
        # Get all lessons in the module for navigation
        module_lessons = Lesson.objects.filter(module=self.object.module).order_by('order')
        lesson_list = list(module_lessons)
        
        # Find current index and get next/previous lessons
        current_index = None
        for i, lesson in enumerate(lesson_list):
            if lesson.id == self.object.id:
                current_index = i
                break
        
        context['previous_lesson'] = lesson_list[current_index - 1] if current_index > 0 else None
        context['next_lesson'] = lesson_list[current_index + 1] if current_index < len(lesson_list) - 1 else None
        context['current_lesson_number'] = current_index + 1 if current_index is not None else 1
        context['total_lessons'] = len(lesson_list)
        context['user_progress'] = user_progress
        context['is_lesson_completed'] = user_progress.is_lesson_completed(self.object)
        context['course'] = course
        
        return context

class RoadmapView(TemplateView):
    template_name = 'courses/roadmap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Group technologies by phase with their courses
        technologies_by_phase = {}
        for tech in Technology.objects.all().prefetch_related('course'):
            if tech.phase not in technologies_by_phase:
                technologies_by_phase[tech.phase] = []
            technologies_by_phase[tech.phase].append(tech)
        
        context['technologies_by_phase'] = technologies_by_phase
        context['total_phases'] = max(technologies_by_phase.keys()) if technologies_by_phase else 0
        
        # Add user progress if authenticated
        if self.request.user.is_authenticated:
            user_courses = UserProgress.objects.filter(user=self.request.user).select_related('course')
            context['user_progress'] = {progress.course_id: progress for progress in user_courses}
        
        return context

@login_required
@require_POST
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as completed or incomplete"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.module.course
    
    # Get or create user progress
    user_progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    action = request.POST.get('action', 'complete')
    
    if action == 'complete':
        completed = user_progress.mark_lesson_complete(lesson)
        message = 'Lesson marked as completed!' if completed else 'Lesson was already completed.'
    else:  # action == 'incomplete'
        completed = user_progress.mark_lesson_incomplete(lesson)
        message = 'Lesson marked as incomplete!' if completed else 'Lesson was already incomplete.'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request - return JSON
        return JsonResponse({
            'status': 'success',
            'message': message,
            'progress_percentage': user_progress.progress_percentage,
            'completed_lessons': user_progress.get_completed_lessons_count(),
            'total_lessons': user_progress.get_total_lessons_count(),
            'is_completed': user_progress.is_lesson_completed(lesson)
        })
    else:
        # Regular form submission
        messages.success(request, message)
        return redirect('lesson_detail', pk=lesson_id)

@login_required
def get_course_progress(request, course_id):
    """Get progress data for a course (AJAX endpoint)"""
    course = get_object_or_404(Course, id=course_id)
    
    try:
        user_progress = UserProgress.objects.get(user=request.user, course=course)
        return JsonResponse({
            'progress_percentage': user_progress.progress_percentage,
            'completed_lessons': user_progress.get_completed_lessons_count(),
            'total_lessons': user_progress.get_total_lessons_count()
        })
    except UserProgress.DoesNotExist:
        return JsonResponse({
            'progress_percentage': 0,
            'completed_lessons': 0,
            'total_lessons': course.lessons_count()
        })