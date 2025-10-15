from django.urls import path

from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('technology/<int:pk>/', views.TechnologyDetailView.as_view(), name='technology_detail'),
    path('lesson/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('roadmap/', views.RoadmapView.as_view(), name='roadmap'),
    
    # Progress tracking URLs
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('course/<int:course_id>/progress/', views.get_course_progress, name='get_course_progress'),

        # Exercise URLs (ADD THESE)
    path('exercise/<int:exercise_id>/validate/', views.validate_exercise_solution, name='validate_exercise'),
    path('exercise/<int:exercise_id>/quiz/', views.submit_quiz_answer, name='submit_quiz_answer'),
    path('exercise/<int:pk>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
]