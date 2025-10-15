from django.views.generic import ListView, DetailView
from django.db.models import Prefetch
from .models import Course, Technology, Lesson, WorkflowDiagram

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modules'] = self.object.modules.prefetch_related('lessons')
        return context

class TechnologyDetailView(DetailView):
    model = Technology
    template_name = 'courses/technology_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workflows'] = WorkflowDiagram.objects.filter(technology=self.object)
        return context

class LessonDetailView(DetailView):
    model = Lesson
    template_name = 'courses/lesson_detail.html'

class RoadmapView(TemplateView):
    template_name = 'courses/roadmap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group technologies by phase
        technologies_by_phase = {}
        for tech in Technology.objects.all():
            if tech.phase not in technologies_by_phase:
                technologies_by_phase[tech.phase] = []
            technologies_by_phase[tech.phase].append(tech)
        
        context['technologies_by_phase'] = technologies_by_phase
        return context
