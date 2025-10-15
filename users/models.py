from django.contrib.auth.models import AbstractUser
from django.db import models

from courses.models import Course


class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    current_phase = models.IntegerField(default=1)
    
    def __str__(self):
        return self.username
    
    def get_active_courses(self):
        """Get all courses the user is actively enrolled in"""
        return Course.objects.filter(userprogress__user=self)
    
    def get_completed_courses(self):
        """Get courses where user has 100% progress"""
        return self.get_active_courses().filter(userprogress__progress_percentage=100)
    
    def get_course_progress(self, course):
        """Get progress for a specific course"""
        try:
            return UserProgress.objects.get(user=self, course=course)
        except UserProgress.DoesNotExist:
            return None

class UserProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    completed_lessons = models.ManyToManyField('courses.Lesson', blank=True)
    progress_percentage = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed_lesson = models.ForeignKey('courses.Lesson', on_delete=models.SET_NULL, null=True, blank=True, related_name='last_accessed_by')
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name_plural = "User Progress"
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.progress_percentage}%)"
    
    def update_progress(self):
        """Calculate and update progress percentage"""
        total_lessons = self.course.lessons_count()
        completed_count = self.completed_lessons.count()
        
        if total_lessons > 0:
            self.progress_percentage = int((completed_count / total_lessons) * 100)
        else:
            self.progress_percentage = 0
        
        self.save()
    
    def is_lesson_completed(self, lesson):
        """Check if a specific lesson is completed"""
        return self.completed_lessons.filter(id=lesson.id).exists()
    
    def mark_lesson_complete(self, lesson):
        """Mark a lesson as completed and update progress"""
        if not self.is_lesson_completed(lesson):
            self.completed_lessons.add(lesson)
            self.last_accessed_lesson = lesson
            self.update_progress()
            return True
        return False
    
    def mark_lesson_incomplete(self, lesson):
        """Mark a lesson as incomplete and update progress"""
        if self.is_lesson_completed(lesson):
            self.completed_lessons.remove(lesson)
            self.update_progress()
            return True
        return False
    
    def get_completed_lessons_count(self):
        """Get count of completed lessons"""
        return self.completed_lessons.count()
    
    def get_total_lessons_count(self):
        """Get total lessons in the course"""
        return self.course.lessons_count()