from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Avg, Sum
from courses.models import Course, Lesson, UserExerciseAttempt
from users.models import UserProgress
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import views as auth_views

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['technologies_count'] = 15  # Will be dynamic later
        context['total_lessons'] = 120      # Will be dynamic later
        return context

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user progress data
        user_progress = UserProgress.objects.filter(user=user).select_related('course')
        
        # Calculate learning statistics
        total_courses = Course.objects.filter(is_active=True).count()
        enrolled_courses = user_progress.count()
        completed_courses = user_progress.filter(progress_percentage=100).count()
        
        # Calculate total learning time
        total_lessons_completed = sum(progress.completed_lessons.count() for progress in user_progress)
        total_learning_minutes = sum(
            progress.completed_lessons.aggregate(total=Sum('duration_minutes'))['total'] or 0 
            for progress in user_progress
        )
        
        # Recent activity (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_activity = UserProgress.objects.filter(
            user=user,
            updated_at__gte=seven_days_ago
        ).order_by('-updated_at')[:10]
        
        # Exercise performance
        exercise_attempts = UserExerciseAttempt.objects.filter(user=user)
        total_exercises = exercise_attempts.count()
        correct_exercises = exercise_attempts.filter(is_correct=True).count()
        exercise_success_rate = (correct_exercises / total_exercises * 100) if total_exercises > 0 else 0
        
        # Current learning phase
        current_phase = self._get_current_learning_phase(user)
        
        context.update({
            'user_progress': user_progress,
            'total_courses': total_courses,
            'enrolled_courses': enrolled_courses,
            'completed_courses': completed_courses,
            'completion_rate': (completed_courses / enrolled_courses * 100) if enrolled_courses > 0 else 0,
            'total_lessons_completed': total_lessons_completed,
            'total_learning_hours': round(total_learning_minutes / 60, 1),
            'recent_activity': recent_activity,
            'exercise_success_rate': round(exercise_success_rate, 1),
            'current_phase': current_phase,
            'streak_days': self._calculate_streak(user),
        })
        return context
    
    def _get_current_learning_phase(self, user):
        """Determine user's current learning phase based on progress"""
        user_progress = UserProgress.objects.filter(user=user).select_related('course__technology')
        
        if not user_progress:
            return 1  # Start with phase 1
        
        # Find the highest phase with incomplete courses
        phases_progress = {}
        for progress in user_progress:
            phase = progress.course.technology.phase
            if phase not in phases_progress:
                phases_progress[phase] = []
            phases_progress[phase].append(progress.progress_percentage)
        
        # Find the first phase that's not 100% complete
        for phase in sorted(phases_progress.keys()):
            avg_progress = sum(phases_progress[phase]) / len(phases_progress[phase])
            if avg_progress < 100:
                return phase
        
        # If all phases are complete, return the next phase
        return max(phases_progress.keys()) + 1 if phases_progress else 1
    
    def _calculate_streak(self, user):
        """Calculate user's learning streak"""
        today = timezone.now().date()
        streak = 0
        
        # Check last 30 days for activity
        for i in range(30):
            check_date = today - timedelta(days=i)
            has_activity = UserProgress.objects.filter(
                user=user,
                updated_at__date=check_date
            ).exists() or UserExerciseAttempt.objects.filter(
                user=user,
                attempted_at__date=check_date
            ).exists()
            
            if has_activity:
                streak += 1
            else:
                break
        
        return streak