from django.db import models
from django.urls import reverse


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
    content = models.TextField(help_text="Markdown supported content")
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES)
    order = models.IntegerField()
    code_examples = models.TextField(blank=True, help_text="JSON formatted code examples")
    video_url = models.URLField(blank=True)
    duration_minutes = models.IntegerField()
    is_free = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

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