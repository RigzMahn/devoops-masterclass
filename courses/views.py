import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView
import json
import re
from .models import InteractiveExercise, UserExerciseAttempt
from users.models import UserProgress


from .models import (
    Course,
    InteractiveExercise,
    Lesson,
    Module,
    Technology,
    UserExerciseAttempt,
    WorkflowDiagram,
)


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
        
        # Calculate progress if user is authenticated
        if self.request.user.is_authenticated:
            user_progress = UserProgress.objects.filter(user=self.request.user).select_related('course')
            progress_dict = {progress.course_id: progress for progress in user_progress}
            context['user_progress'] = progress_dict
            
            # Calculate overall progress
            total_courses = Course.objects.filter(is_active=True).count()
            completed_courses = user_progress.filter(progress_percentage=100).count()
            context['overall_progress'] = int((completed_courses / total_courses) * 100) if total_courses > 0 else 0
            
            # Calculate phase progress
            phase_progress = {}
            for phase, techs in technologies_by_phase.items():
                phase_courses = [tech.course for tech in techs if hasattr(tech, 'course')]
                completed_in_phase = sum(1 for course in phase_courses if course.id in progress_dict and progress_dict[course.id].progress_percentage == 100)
                phase_progress[phase] = int((completed_in_phase / len(phase_courses)) * 100) if phase_courses else 0
            
            context['phase_progress'] = phase_progress
        
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


# === INTERACTIVE EXERCISE VIEWS ===

@login_required
@require_POST
@csrf_exempt
def validate_exercise_solution(request, exercise_id):
    """Validate user's code solution against test cases"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_code = data.get('code', '').strip()
        exercise = get_object_or_404(InteractiveExercise, id=exercise_id)
        
        # Get or create user attempt
        attempt, created = UserExerciseAttempt.objects.get_or_create(
            user=request.user,
            exercise=exercise,
            defaults={
                'code_submission': user_code,
                'attempted_at': timezone.now()
            }
        )
        
        if not created:
            # Update existing attempt
            attempt.code_submission = user_code
            attempt.attempted_at = timezone.now()
        
        # Validate based on exercise type
        if exercise.exercise_type == 'code':
            validation_result = validate_code_exercise(user_code, exercise)
        elif exercise.exercise_type == 'quiz':
            user_answers = data.get('answers', {})
            validation_result = validate_quiz_exercise(user_answers, exercise)
        else:
            validation_result = {
                'success': False,
                'message': 'Exercise type not supported yet'
            }
        
        # Update attempt record
        attempt.is_correct = validation_result['success']
        attempt.score = validation_result.get('score', 0)
        attempt.answers = validation_result.get('answers', {})
        
        if validation_result['success']:
            attempt.completed_at = timezone.now()
        
        attempt.save()
        
        return JsonResponse(validation_result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Server error: {str(e)}'
        }, status=500)

def validate_code_exercise(user_code, exercise):
    """Validate code exercise with proper testing"""
    # Basic validation - check if code is not empty
    if not user_code.strip():
        return {
            'success': False,
            'message': 'Code cannot be empty',
            'score': 0
        }
    
    # Check against solution (basic exact match for now)
    solution_code = exercise.solution_code.strip()
    
    # Normalize code for comparison (remove extra whitespace)
    normalized_user_code = re.sub(r'\s+', ' ', user_code.strip())
    normalized_solution = re.sub(r'\s+', ' ', solution_code.strip())
    
    is_exact_match = normalized_user_code == normalized_solution
    
    if is_exact_match:
        return {
            'success': True,
            'message': 'Excellent! Your solution matches the expected code.',
            'score': exercise.points,
            'max_score': exercise.points
        }
    else:
        # Provide helpful feedback
        user_lines = user_code.split('\n')
        solution_lines = solution_code.split('\n')
        
        feedback = "Your solution is close but needs some adjustments. "
        
        # Basic line count check
        if len(user_lines) != len(solution_lines):
            feedback += f"Expected {len(solution_lines)} lines, got {len(user_lines)}. "
        
        # Check for key elements in code
        key_elements = find_key_elements(solution_code)
        missing_elements = []
        
        for element in key_elements:
            if element not in user_code:
                missing_elements.append(element)
        
        if missing_elements:
            feedback += f"Missing key elements: {', '.join(missing_elements)}. "
        
        return {
            'success': False,
            'message': feedback,
            'score': max(0, exercise.points - len(missing_elements) * 2),
            'max_score': exercise.points,
            'hint': 'Compare your code with the expected structure and check for syntax errors.'
        }

def find_key_elements(code):
    """Find key programming elements in code for feedback"""
    elements = []
    
    # Common Git commands
    git_commands = ['git init', 'git add', 'git commit', 'git push', 'git pull']
    for cmd in git_commands:
        if cmd in code:
            elements.append(cmd)
    
    # Common Docker commands
    docker_commands = ['FROM', 'RUN', 'COPY', 'WORKDIR', 'EXPOSE', 'CMD']
    for cmd in docker_commands:
        if cmd in code:
            elements.append(f'Docker {cmd}')
    
    # Common file operations
    file_ops = ['open(', 'read(', 'write(', 'import ', 'def ', 'class ']
    for op in file_ops:
        if op in code:
            elements.append(op.strip())
    
    return elements

def validate_quiz_exercise(user_answers, exercise):
    """Validate quiz exercise answers"""
    if not exercise.options or 'correct_answer' not in exercise.options:
        return {
            'success': False,
            'message': 'Exercise configuration error',
            'score': 0
        }
    
    correct_answer = exercise.options.get('correct_answer')
    user_answer = user_answers.get('answer')
    
    is_correct = str(user_answer) == str(correct_answer)
    
    if is_correct:
        return {
            'success': True,
            'message': 'Correct answer! Well done.',
            'score': exercise.points,
            'max_score': exercise.points,
            'answers': {'user_answer': user_answer, 'correct_answer': correct_answer}
        }
    else:
        return {
            'success': False,
            'message': f'Incorrect. The right answer is: {correct_answer}',
            'score': 0,
            'max_score': exercise.points,
            'answers': {'user_answer': user_answer, 'correct_answer': correct_answer}
        }

@login_required
def submit_quiz_answer(request, exercise_id):
    """Handle quiz answer submissions"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_answer = data.get('answer')
            exercise = get_object_or_404(InteractiveExercise, id=exercise_id)
            
            # Validate quiz answer
            result = validate_quiz_exercise({'answer': user_answer}, exercise)
            
            # Record attempt
            attempt, created = UserExerciseAttempt.objects.get_or_create(
                user=request.user,
                exercise=exercise,
                defaults={
                    'answers': {'answer': user_answer},
                    'is_correct': result['success'],
                    'score': result['score'],
                    'completed_at': timezone.now() if result['success'] else None
                }
            )
            
            if not created:
                attempt.answers = {'answer': user_answer}
                attempt.is_correct = result['success']
                attempt.score = result['score']
                if result['success']:
                    attempt.completed_at = timezone.now()
                attempt.save()
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error processing quiz: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

class ExerciseDetailView(LoginRequiredMixin, DetailView):
    model = InteractiveExercise
    template_name = 'courses/exercise_detail.html'
    context_object_name = 'exercise'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_attempt'] = UserExerciseAttempt.objects.filter(
            user=self.request.user,
            exercise=self.object
        ).first()
        return context


class SearchView(ListView):
    model = Course
    template_name = 'courses/search_results.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        technology_filter = self.request.GET.get('technology', '')
        difficulty_filter = self.request.GET.get('difficulty', '')
        duration_filter = self.request.GET.get('duration', '')
        
        queryset = Course.objects.filter(is_active=True).select_related('technology')
        
        # Text search
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(technology__name__icontains=query) |
                Q(technology__description__icontains=query)
            )
        
        # Technology filter
        if technology_filter:
            queryset = queryset.filter(technology__category=technology_filter)
        
        # Difficulty filter
        if difficulty_filter:
            queryset = queryset.filter(difficulty=difficulty_filter)
        
        # Duration filter
        if duration_filter:
            if duration_filter == 'short':
                queryset = queryset.filter(estimated_duration__lte=5)
            elif duration_filter == 'medium':
                queryset = queryset.filter(estimated_duration__gt=5, estimated_duration__lte=10)
            elif duration_filter == 'long':
                queryset = queryset.filter(estimated_duration__gt=10)
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        
        context.update({
            'search_query': query,
            'technology_filter': self.request.GET.get('technology', ''),
            'difficulty_filter': self.request.GET.get('difficulty', ''),
            'duration_filter': self.request.GET.get('duration', ''),
            'total_results': self.get_queryset().count(),
            'technologies': Technology.TECHNOLOGY_CATEGORIES,
            'durations': [
                ('short', 'Short (0-5 hours)'),
                ('medium', 'Medium (5-10 hours)'),
                ('long', 'Long (10+ hours)')
            ]
        })
        return context

def search_suggestions(request):
    """AJAX endpoint for search suggestions"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Search in courses and technologies
    course_suggestions = Course.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    ).values('title', 'id')[:5]
    
    technology_suggestions = Technology.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    ).values('name', 'id')[:5]
    
    suggestions = []
    
    for course in course_suggestions:
        suggestions.append({
            'type': 'course',
            'text': course['title'],
            'url': f"/courses/{course['id']}/"
        })
    
    for tech in technology_suggestions:
        suggestions.append({
            'type': 'technology',
            'text': tech['name'],
            'url': f"/courses/technology/{tech['id']}/"
        })
    
    return JsonResponse({'suggestions': suggestions})