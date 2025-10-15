from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


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
        # Add user progress data later
        return context

class RoadmapView(TemplateView):
    template_name = 'roadmap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add roadmap data later
        return context
