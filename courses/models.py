from django.db import models
from django.utils import timezone
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field


class Technology(models.Model):
    TECHNOLOGY_CATEGORIES = [
        ('vcs', 'Version Control'),
        ('ci_cd', 'CI/CD'),
        ('container', 'Containerization'),
        ('orchestration', 'Orchestration'),
        ('iac', 'Infrastructure as Code'),
        ('monitoring', 'Monitoring'),
        ('security', 'Security'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=TECHNOLOGY_CATEGORIES)
    description = models.TextField()
    logo = models.ImageField(upload_to='technology_logos/', blank=True)
    official_docs_url = models.URLField(blank=True)
    phase = models.IntegerField(help_text="Learning phase number")
    order = models.IntegerField(help_text="Order within phase")
    
    class Meta:
        ordering = ['phase', 'order']
        verbose_name_plural = "Technologies"
    
    def __str__(self):
        return self.name

class Course(models.Model):
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    technology = models.OneToOneField(Technology, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    estimated_duration = models.IntegerField(help_text="Duration in hours")
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'pk': self.pk})
    
    def lesson_count(self):
        return Lesson.objects.filter(module__course=self).count()
    
    def total_duration(self):
        from django.db.models import Sum
        total_minutes = Lesson.objects.filter(module__course=self).aggregate(Sum('duration_minutes'))['total'] or 0
        return total_minutes // 60 # Return hours

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    LESSON_TYPES = [
        ('theory', 'Theory'),
        ('practice', 'Hands-on Practice'),
        ('quiz', 'Quiz'),
        ('project', 'Project'),
    ]
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    # content = models.TextField(help_text="Markdown supported content")
    content = CKEditor5Field('Content', config_name='extends')
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES)
    order = models.IntegerField()
    example_code_data = models.TextField(blank=True, help_text="JSON formatted code examples")
    video_url = models.URLField(blank=True)
    duration_minutes = models.IntegerField()
    is_free = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class CodeExample(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('bash', 'Bash'),
        ('yaml', 'YAML'),
        ('dockerfile', 'Dockerfile'),
        ('json', 'JSON'),
        ('sql', 'SQL'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('c', 'C'),
        ('c++', 'C++'),
        ('c#', 'C#'),
        ('ruby', 'Ruby'),
        ('php', 'PHP'),
        ('swift', 'Swift'),
        ('go', 'Go'),
        ('rust', 'Rust'),
        ('typescript', 'TypeScript'),
        ('kotlin', 'Kotlin'),
        ('scala', 'Scala'),
        ('perl', 'Perl'),
        ('elixir', 'Elixir'),
        ('crystal', 'Crystal'),
        ('r', 'R'),
        ('julia', 'Julia'),
        ('haskell', 'Haskell'),
        ('lua', 'Lua'),
        ('dart', 'Dart'),
    ]
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='code_examples')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Brief description of the code example")
    code = models.TextField()
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='python')
    explanation = CKEditor5Field('Explanation', config_name='default', blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

class WorkflowDiagram(models.Model):
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    diagram_data = models.TextField(help_text="Mermaid.js or similar diagram data")
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.technology.name} - {self.title}"
    
class InteractiveExercise(models.Model):
    EXERCISE_TYPES = [
        ('code', 'Code Exercise'),
        ('quiz', 'Multiple Choice Quiz'),
        ('matching', 'Matching Exercise'),
        ('fill_blank', 'Fill in the Blanks'),
    ]
    
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='interactive_exercises')
    title = models.CharField(max_length=200)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    instructions = CKEditor5Field('Instructions', config_name='default')
    initial_code = models.TextField(blank=True, help_text="Initial code for code exercises")
    solution_code = models.TextField(blank=True, help_text="Expected solution for code exercises")
    test_cases = models.JSONField(blank=True, null=True, help_text="Test cases for validation")
    options = models.JSONField(blank=True, null=True, help_text="Options for quiz/matching exercises")
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Interactive Exercise'
        verbose_name_plural = 'Interactive Exercises'
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"
    
    def get_language_extension(self):
        """Get file extension based on exercise content"""
        if 'docker' in self.initial_code.lower() or 'FROM' in self.initial_code:
            return 'Dockerfile'
        elif 'apiVersion:' in self.initial_code:
            return 'yaml'
        elif 'pipeline' in self.initial_code:
            return 'groovy'
        else:
            return 'txt'
    
    def get_total_attempts(self):
        """Get total number of attempts for this exercise"""
        return self.attempts.count()
    
    def get_success_rate(self):
        """Calculate success rate for this exercise"""
        total_attempts = self.get_total_attempts()
        if total_attempts == 0:
            return 0
        successful_attempts = self.attempts.filter(is_correct=True).count()
        return (successful_attempts / total_attempts) * 100

class UserExerciseAttempt(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    exercise = models.ForeignKey(InteractiveExercise, on_delete=models.CASCADE)
    code_submission = models.TextField(blank=True)
    answers = models.JSONField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    attempted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'exercise']
        verbose_name = 'User Exercise Attempt'
        verbose_name_plural = 'User Exercise Attempts'    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.title}"


class DiscussionForum(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='forum')
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Forum: {self.course.title}"

class DiscussionThread(models.Model):
    forum = models.ForeignKey(DiscussionForum, on_delete=models.CASCADE, related_name='threads')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = CKEditor5Field('Content', config_name='extends')
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
        verbose_name = 'Discussion Thread'
        verbose_name_plural = 'Discussion Threads'    
    def __str__(self):
        return self.title

class DiscussionPost(models.Model):
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    content = CKEditor5Field('Content', config_name='extends')
    is_answer = models.BooleanField(default=False)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_answer', 'created_at']
        verbose_name = 'Discussion Post'
        verbose_name_plural = 'Discussion Posts'    
    def __str__(self):
        return f"Post by {self.user.username} in {self.thread.title}"
    
    def net_votes(self):
        return self.upvotes - self.downvotes

class UserVote(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=10, choices=[('up', 'Upvote'), ('down', 'Downvote')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        verbose_name = 'User Vote'
        verbose_name_plural = 'User Votes'

class UserExerciseAttempt(models.Model):
    """Tracks user attempts and progress on interactive exercises"""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='exercise_attempts')
    exercise = models.ForeignKey('InteractiveExercise', on_delete=models.CASCADE, related_name='attempts')
    code_submission = models.TextField(blank=True, help_text="User's code submission for code exercises")
    answers = models.JSONField(blank=True, null=True, help_text="User's answers for quiz exercises")
    is_correct = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    attempted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'exercise']
        ordering = ['-attempted_at']
        verbose_name = 'Exercise Attempt'
        verbose_name_plural = 'Exercise Attempts'
    
    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{status} {self.user.username} - {self.exercise.title} ({self.score} pts)"
    
    def mark_completed(self, is_correct=True, score=None):
        """Mark attempt as completed"""
        self.is_correct = is_correct
        self.score = score or self.exercise.points if is_correct else 0
        self.completed_at = timezone.now()
        self.save()
    
    def get_time_spent(self):
        """Calculate time spent on the exercise"""
        if self.completed_at and self.attempted_at:
            return self.completed_at - self.attempted_at
        return None
