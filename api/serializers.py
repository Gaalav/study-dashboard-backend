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
        # Convert to camelCase for frontend
        data['startTime'] = str(data.pop('start_time', ''))[:5]
        data['endTime'] = str(data.pop('end_time', ''))[:5]
        return data
    
    def to_internal_value(self, data):
        # Convert camelCase to snake_case
        internal = {}
        internal['start_time'] = data.get('startTime') or data.get('start_time')
        internal['end_time'] = data.get('endTime') or data.get('end_time')
        internal['subject'] = data.get('subject')
        internal['status'] = data.get('status', 'upcoming')
        internal['date'] = data.get('date')
        return super().to_internal_value(internal)


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
    # Explicitly declare fields to control validation
    link = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'subject', 'due_date', 'status', 'description', 'link']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Convert to camelCase for frontend
        data['dueDate'] = data.pop('due_date')
        return data
    
    def to_internal_value(self, data):
        # Convert camelCase to snake_case
        internal = {}
        internal['title'] = data.get('title')
        internal['subject'] = data.get('subject')
        internal['due_date'] = data.get('dueDate') or data.get('due_date')
        internal['status'] = data.get('status', 'pending')
        internal['description'] = data.get('description', '')
        # Handle empty link - set to None instead of empty string for URLField
        link = data.get('link', '')
        internal['link'] = link if link else None
        return super().to_internal_value(internal)


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
