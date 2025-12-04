from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    ScheduleItem, Quiz, QuizQuestion, QuizAttempt,
    Assignment, WeeklyGoal, StudyActivity, SubjectPerformance, Exam
)
from .serializers import (
    ScheduleItemSerializer, QuizSerializer, QuizListSerializer,
    QuizQuestionSerializer, QuizAttemptSerializer,
    AssignmentSerializer, WeeklyGoalSerializer, StudyActivitySerializer,
    SubjectPerformanceSerializer, ExamSerializer
)


# Authentication Views
@api_view(['POST'])
def login_view(request):
    """Login endpoint that returns a token"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'message': 'Login successful'
        })
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def verify_token(request):
    """Verify if the token is valid"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    if auth_header.startswith('Token '):
        token_key = auth_header.split(' ')[1]
        try:
            token = Token.objects.get(key=token_key)
            return Response({'valid': True, 'username': token.user.username})
        except Token.DoesNotExist:
            pass
    
    return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_view(request):
    """Logout endpoint that deletes the token"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    if auth_header.startswith('Token '):
        token_key = auth_header.split(' ')[1]
        try:
            token = Token.objects.get(key=token_key)
            token.delete()
        except Token.DoesNotExist:
            pass
    
    return Response({'message': 'Logged out successfully'})


class ScheduleItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing schedule items"""
    queryset = ScheduleItem.objects.all()
    serializer_class = ScheduleItemSerializer
    
    def get_queryset(self):
        queryset = ScheduleItem.objects.all()
        date = self.request.query_params.get('date', None)
        
        if date:
            queryset = queryset.filter(date=date)
        else:
            # Default to today's schedule
            queryset = queryset.filter(date=timezone.now().date())
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's schedule"""
        today = timezone.now().date()
        items = ScheduleItem.objects.filter(date=today)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark a schedule item as completed"""
        item = self.get_object()
        item.status = 'completed'
        item.save()
        serializer = self.get_serializer(item)
        return Response(serializer.data)


class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet for managing quizzes"""
    queryset = Quiz.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return QuizListSerializer
        return QuizSerializer
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming quizzes"""
        today = timezone.now().date()
        quizzes = Quiz.objects.filter(quiz_date__gte=today)
        serializer = QuizListSerializer(quizzes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit quiz answers and calculate score"""
        quiz = self.get_object()
        answers = request.data.get('answers', {})
        
        # Calculate score
        score = 0
        questions = quiz.questions.all()
        total = questions.count()
        
        for question in questions:
            user_answer = answers.get(str(question.id))
            if user_answer is not None and int(user_answer) == question.correct_answer:
                score += 1
        
        # Save attempt
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            score=score,
            total_questions=total,
            answers=answers
        )
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)


class QuizQuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing quiz questions"""
    queryset = QuizQuestion.objects.all()
    serializer_class = QuizQuestionSerializer
    
    def get_queryset(self):
        queryset = QuizQuestion.objects.all()
        quiz_id = self.request.query_params.get('quiz', None)
        
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
        
        return queryset


class AssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing assignments"""
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get assignment statistics"""
        total = Assignment.objects.count()
        completed = Assignment.objects.filter(status='completed').count()
        remaining = total - completed
        
        return Response({
            'completed': completed,
            'total': total,
            'remaining': remaining
        })
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark an assignment as completed"""
        assignment = self.get_object()
        assignment.status = 'completed'
        assignment.save()
        serializer = self.get_serializer(assignment)
        return Response(serializer.data)


class WeeklyGoalViewSet(viewsets.ModelViewSet):
    """ViewSet for managing weekly goals"""
    queryset = WeeklyGoal.objects.all()
    serializer_class = WeeklyGoalSerializer
    
    def get_queryset(self):
        queryset = WeeklyGoal.objects.all()
        
        # Filter by current week by default
        current_week = self.request.query_params.get('current_week', 'true')
        if current_week.lower() == 'true':
            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())
            queryset = queryset.filter(week_start=week_start)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update goal status"""
        goal = self.get_object()
        new_status = request.data.get('status')
        if new_status in ['pending', 'in-progress', 'completed']:
            goal.status = new_status
            goal.save()
            serializer = self.get_serializer(goal)
            return Response(serializer.data)
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)


class StudyActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for managing study activities"""
    queryset = StudyActivity.objects.all()
    serializer_class = StudyActivitySerializer
    
    def get_queryset(self):
        queryset = StudyActivity.objects.all()
        limit = self.request.query_params.get('limit', None)
        
        if limit:
            queryset = queryset[:int(limit)]
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent activities (last 10)"""
        activities = StudyActivity.objects.all()[:10]
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)


class SubjectPerformanceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing subject performance"""
    queryset = SubjectPerformance.objects.all()
    serializer_class = SubjectPerformanceSerializer


class ExamViewSet(viewsets.ModelViewSet):
    """ViewSet for managing exams"""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming exams"""
        today = timezone.now().date()
        exams = Exam.objects.filter(exam_date__gte=today)
        serializer = self.get_serializer(exams, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def dashboard_overview(request):
    """Get all dashboard data in a single request"""
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    # Get all relevant data
    schedule = ScheduleItem.objects.filter(date=today)
    upcoming_quiz = Quiz.objects.filter(quiz_date__gte=today).first()
    upcoming_exam = Exam.objects.filter(exam_date__gte=today).first()
    assignments = Assignment.objects.all()
    goals = WeeklyGoal.objects.filter(week_start=week_start)
    activities = StudyActivity.objects.all()[:5]
    performance = SubjectPerformance.objects.all()
    
    # Calculate assignment stats
    total_assignments = assignments.count()
    completed_assignments = assignments.filter(status='completed').count()
    
    return Response({
        'schedule': ScheduleItemSerializer(schedule, many=True).data,
        'upcomingQuiz': QuizListSerializer(upcoming_quiz).data if upcoming_quiz else None,
        'upcomingExam': ExamSerializer(upcoming_exam).data if upcoming_exam else None,
        'assignments': {
            'completed': completed_assignments,
            'total': total_assignments,
            'remaining': total_assignments - completed_assignments
        },
        'weeklyGoals': WeeklyGoalSerializer(goals, many=True).data,
        'recentActivities': StudyActivitySerializer(activities, many=True).data,
        'subjectPerformance': SubjectPerformanceSerializer(performance, many=True).data
    })
