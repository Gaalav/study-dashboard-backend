from rest_framework import serializers
from .models import (
    ScheduleItem, Quiz, QuizQuestion, QuizAttempt,
    Assignment, WeeklyGoal, StudyActivity, SubjectPerformance, Exam
)


class ScheduleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleItem
        fields = ['id', 'start_time', 'end_time', 'subject', 'status', 'date']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format times for frontend compatibility
        data['startTime'] = data.pop('start_time')
        data['endTime'] = data.pop('end_time')
        return data
    
    def to_internal_value(self, data):
        # Handle camelCase from frontend
        if 'startTime' in data:
            data['start_time'] = data.pop('startTime')
        if 'endTime' in data:
            data['end_time'] = data.pop('endTime')
        return super().to_internal_value(data)


class QuizQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    correctAnswer = serializers.IntegerField(source='correct_answer')
    
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question_text', 'options', 'correctAnswer', 'explanation', 'order']
    
    def get_options(self, obj):
        return [obj.option_a, obj.option_b, obj.option_c, obj.option_d]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['question'] = data.pop('question_text')
        return data


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    daysUntil = serializers.IntegerField(source='days_until', read_only=True)
    timeLimit = serializers.IntegerField(source='time_limit')
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'subject', 'topic', 'quiz_date', 'timeLimit', 'daysUntil', 'questions']


class QuizListSerializer(serializers.ModelSerializer):
    """Simplified serializer for quiz list view"""
    daysUntil = serializers.IntegerField(source='days_until', read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'subject', 'topic', 'quiz_date', 'daysUntil']


class QuizAttemptSerializer(serializers.ModelSerializer):
    percentage = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'score', 'total_questions', 'answers', 'completed_at', 'percentage']


class AssignmentSerializer(serializers.ModelSerializer):
    dueDate = serializers.DateField(source='due_date')
    
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'subject', 'dueDate', 'status', 'description', 'link']


class WeeklyGoalSerializer(serializers.ModelSerializer):
    weekStart = serializers.DateField(source='week_start')
    
    class Meta:
        model = WeeklyGoal
        fields = ['id', 'text', 'status', 'weekStart']


class StudyActivitySerializer(serializers.ModelSerializer):
    activityTime = serializers.DateTimeField(source='activity_time')
    
    class Meta:
        model = StudyActivity
        fields = ['id', 'text', 'activityTime']


class SubjectPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectPerformance
        fields = ['id', 'subject', 'grade', 'percentage']


class ExamSerializer(serializers.ModelSerializer):
    daysUntil = serializers.IntegerField(source='days_until', read_only=True)
    examDate = serializers.DateField(source='exam_date')
    
    class Meta:
        model = Exam
        fields = ['id', 'title', 'subject', 'examDate', 'daysUntil']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    assignments_completed = serializers.IntegerField()
    assignments_total = serializers.IntegerField()
    assignments_remaining = serializers.IntegerField()
