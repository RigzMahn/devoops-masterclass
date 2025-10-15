from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('technology/<int:pk>/', views.TechnologyDetailView.as_view(), name='technology_detail'),
    path('lesson/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('roadmap/', views.RoadmapView.as_view(), name='roadmap'),
]
