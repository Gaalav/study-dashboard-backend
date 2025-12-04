from rest_framework import serializers
from .models import (
    ScheduleItem, Quiz, QuizQuestion, QuizAttempt,
    Assignment, WeeklyGoal, StudyActivity, SubjectPerformance, Exam
)


class ScheduleItemSerializer(serializers.ModelSerializer):
    # Accept both snake_case and camelCase
    startTime = serializers.TimeField(source='start_time', required=False)
    endTime = serializers.TimeField(source='end_time', required=False)
    
    class Meta:
        model = ScheduleItem
        fields = ['id', 'start_time', 'end_time', 'startTime', 'endTime', 'subject', 'status', 'date']
        extra_kwargs = {
            'start_time': {'required': False},
            'end_time': {'required': False},
        }
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format times for frontend compatibility (camelCase)
        data['startTime'] = str(data.get('start_time', ''))[:5] if data.get('start_time') else ''
        data['endTime'] = str(data.get('end_time', ''))[:5] if data.get('end_time') else ''
        # Remove snake_case versions
        data.pop('start_time', None)
        data.pop('end_time', None)
        return data
    
    def to_internal_value(self, data):
        # Create a mutable copy
        mutable_data = dict(data)
        # Handle camelCase from frontend
        if 'startTime' in mutable_data and 'start_time' not in mutable_data:
            mutable_data['start_time'] = mutable_data.get('startTime')
        if 'endTime' in mutable_data and 'end_time' not in mutable_data:
            mutable_data['end_time'] = mutable_data.get('endTime')
        return super().to_internal_value(mutable_data)


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
    dueDate = serializers.DateField(source='due_date', required=False)
    
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'subject', 'dueDate', 'due_date', 'status', 'description', 'link']
        extra_kwargs = {
            'due_date': {'required': False},
        }
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure camelCase for frontend
        if 'due_date' in data:
            data['dueDate'] = data.pop('due_date')
        return data
    
    def to_internal_value(self, data):
        mutable_data = dict(data)
        # Handle camelCase from frontend
        if 'dueDate' in mutable_data and 'due_date' not in mutable_data:
            mutable_data['due_date'] = mutable_data.get('dueDate')
        return super().to_internal_value(mutable_data)


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
