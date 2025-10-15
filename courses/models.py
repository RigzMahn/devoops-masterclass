from django.db import models
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
