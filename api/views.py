from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
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


# Helper to get user from token
def get_user_from_request(request):
    """Extract user from authorization header"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Token '):
        token_key = auth_header.split(' ')[1]
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            pass
    return None


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


# Base ViewSet with user filtering
class UserFilteredViewSet(viewsets.ModelViewSet):
    """Base ViewSet that filters by authenticated user"""
    authentication_classes = [TokenAuthentication]
    permission_classes = []  # Allow any - we'll handle user filtering manually
    
    def get_queryset(self):
        """Filter queryset to only show user's data if authenticated"""
        queryset = super().get_queryset()
        # Filter by user if authenticated
        if self.request.user and self.request.user.is_authenticated:
            try:
                return queryset.filter(user=self.request.user)
            except Exception as e:
                print(f"Error filtering by user: {e}")
        return queryset
    
    def perform_create(self, serializer):
        """Set user when creating new objects if authenticated"""
        if self.request.user and self.request.user.is_authenticated:
            try:
                serializer.save(user=self.request.user)
                return
            except Exception as e:
                print(f"Error saving with user: {e}")
        serializer.save()


class ScheduleItemViewSet(UserFilteredViewSet):
    """ViewSet for managing schedule items"""
    queryset = ScheduleItem.objects.all()
    serializer_class = ScheduleItemSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
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
        items = self.get_queryset().filter(date=today)
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


class QuizViewSet(UserFilteredViewSet):
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
        quizzes = self.get_queryset().filter(quiz_date__gte=today)
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
        
        # Save attempt with user
        attempt = QuizAttempt.objects.create(
            user=request.user,
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filter to only show questions from user's quizzes
        queryset = QuizQuestion.objects.filter(quiz__user=self.request.user)
        quiz_id = self.request.query_params.get('quiz', None)
        
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
        
        return queryset


class AssignmentViewSet(UserFilteredViewSet):
    """ViewSet for managing assignments"""
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get assignment statistics"""
        user_assignments = self.get_queryset()
        total = user_assignments.count()
        completed = user_assignments.filter(status='completed').count()
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


class WeeklyGoalViewSet(UserFilteredViewSet):
    """ViewSet for managing weekly goals"""
    queryset = WeeklyGoal.objects.all()
    serializer_class = WeeklyGoalSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
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


class StudyActivityViewSet(UserFilteredViewSet):
    """ViewSet for managing study activities"""
    queryset = StudyActivity.objects.all()
    serializer_class = StudyActivitySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit', None)
        
        if limit:
            queryset = queryset[:int(limit)]
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent activities (last 10)"""
        activities = self.get_queryset()[:10]
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)


class SubjectPerformanceViewSet(UserFilteredViewSet):
    """ViewSet for managing subject performance"""
    queryset = SubjectPerformance.objects.all()
    serializer_class = SubjectPerformanceSerializer


class ExamViewSet(UserFilteredViewSet):
    """ViewSet for managing exams"""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming exams"""
        today = timezone.now().date()
        exams = self.get_queryset().filter(exam_date__gte=today)
        serializer = self.get_serializer(exams, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def dashboard_overview(request):
    """Get all dashboard data in a single request"""
    user = get_user_from_request(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    # Get all relevant data for THIS USER only
    schedule = ScheduleItem.objects.filter(user=user, date=today)
    upcoming_quiz = Quiz.objects.filter(user=user, quiz_date__gte=today).first()
    upcoming_exam = Exam.objects.filter(user=user, exam_date__gte=today).first()
    assignments = Assignment.objects.filter(user=user)
    goals = WeeklyGoal.objects.filter(user=user, week_start=week_start)
    activities = StudyActivity.objects.filter(user=user)[:5]
    performance = SubjectPerformance.objects.filter(user=user)
    
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


# Cloudflare R2 PDF Upload
@api_view(['POST'])
def upload_pdf(request):
    """Upload PDF to Cloudflare R2 storage"""
    import boto3
    from botocore.config import Config
    import os
    import uuid
    
    user = get_user_from_request(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    
    # Validate file type
    if not file.name.lower().endswith('.pdf'):
        return Response({'error': 'Only PDF files allowed'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (50MB max)
    if file.size > 50 * 1024 * 1024:
        return Response({'error': 'File too large. Max 50MB'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get R2 credentials from environment
    account_id = os.environ.get('R2_ACCOUNT_ID')
    access_key = os.environ.get('R2_ACCESS_KEY_ID')
    secret_key = os.environ.get('R2_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('R2_BUCKET_NAME', 'study-dashboard-pdfs')
    public_url = os.environ.get('R2_PUBLIC_URL', '')
    
    if not all([account_id, access_key, secret_key]):
        return Response({'error': 'R2 storage not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        # Create S3 client for R2
        s3 = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        
        # Generate unique filename
        subject_id = request.data.get('subject_id', 'general')
        file_ext = file.name.split('.')[-1]
        unique_name = f"{subject_id}/{uuid.uuid4().hex}.{file_ext}"
        
        # Upload file
        s3.upload_fileobj(
            file,
            bucket_name,
            unique_name,
            ExtraArgs={
                'ContentType': 'application/pdf',
            }
        )
        
        # Generate URL
        if public_url:
            file_url = f"{public_url}/{unique_name}"
        else:
            # Generate presigned URL (valid for 7 days)
            file_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': unique_name},
                ExpiresIn=604800  # 7 days
            )
        
        return Response({
            'success': True,
            'url': file_url,
            'filename': file.name
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

