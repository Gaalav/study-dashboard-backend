from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'schedule', views.ScheduleItemViewSet)
router.register(r'quizzes', views.QuizViewSet)
router.register(r'quiz-questions', views.QuizQuestionViewSet)
router.register(r'assignments', views.AssignmentViewSet)
router.register(r'goals', views.WeeklyGoalViewSet)
router.register(r'activities', views.StudyActivityViewSet)
router.register(r'performance', views.SubjectPerformanceViewSet)
router.register(r'exams', views.ExamViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard_overview, name='dashboard-overview'),
]
