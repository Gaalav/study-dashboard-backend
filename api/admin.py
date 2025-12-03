from django.contrib import admin
from .models import (
    ScheduleItem, Quiz, QuizQuestion, QuizAttempt,
    Assignment, WeeklyGoal, StudyActivity, SubjectPerformance, Exam
)


@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ['subject', 'start_time', 'end_time', 'status', 'date']
    list_filter = ['status', 'date']
    search_fields = ['subject']


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'topic', 'quiz_date', 'days_until']
    list_filter = ['subject', 'quiz_date']
    search_fields = ['title', 'subject', 'topic']
    inlines = [QuizQuestionInline]


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_text', 'correct_answer', 'order']
    list_filter = ['quiz']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'score', 'total_questions', 'percentage', 'completed_at']
    list_filter = ['quiz', 'completed_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'due_date', 'status']
    list_filter = ['status', 'subject', 'due_date']
    search_fields = ['title', 'subject']


@admin.register(WeeklyGoal)
class WeeklyGoalAdmin(admin.ModelAdmin):
    list_display = ['text', 'status', 'week_start']
    list_filter = ['status', 'week_start']


@admin.register(StudyActivity)
class StudyActivityAdmin(admin.ModelAdmin):
    list_display = ['text', 'activity_time']
    list_filter = ['activity_time']


@admin.register(SubjectPerformance)
class SubjectPerformanceAdmin(admin.ModelAdmin):
    list_display = ['subject', 'grade', 'percentage']
    list_filter = ['grade']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'exam_date', 'days_until']
    list_filter = ['subject', 'exam_date']
