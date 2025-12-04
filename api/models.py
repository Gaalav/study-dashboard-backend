from django.db import models
from django.utils import timezone


class ScheduleItem(models.Model):
    """Model for daily schedule items/classes"""
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.subject} ({self.start_time} - {self.end_time})"


class Quiz(models.Model):
    """Model for upcoming quizzes"""
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    topic = models.CharField(max_length=200)
    quiz_date = models.DateField()
    time_limit = models.IntegerField(default=15, help_text="Time limit in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['quiz_date']

    def __str__(self):
        return f"{self.title} - {self.subject}"

    @property
    def days_until(self):
        """Calculate days until the quiz"""
        delta = self.quiz_date - timezone.now().date()
        return max(0, delta.days)


class QuizQuestion(models.Model):
    """Model for quiz questions"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.IntegerField(choices=[(0, 'A'), (1, 'B'), (2, 'C'), (3, 'D')])
    explanation = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order + 1}: {self.question_text[:50]}..."


class QuizAttempt(models.Model):
    """Model to track quiz attempts and scores"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.IntegerField()
    total_questions = models.IntegerField()
    answers = models.JSONField(default=dict)  # Store user's answers
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt on {self.quiz.title}: {self.score}/{self.total_questions}"

    @property
    def percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100)


class Assignment(models.Model):
    """Model for tracking assignments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    link = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.title} - {self.subject}"


class WeeklyGoal(models.Model):
    """Model for weekly goals"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    text = models.CharField(max_length=300)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    week_start = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-week_start', 'status']

    def __str__(self):
        return f"{self.text[:50]}... ({self.status})"


class StudyActivity(models.Model):
    """Model for tracking study activities"""
    text = models.CharField(max_length=300)
    activity_time = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Study Activities"
        ordering = ['-activity_time']

    def __str__(self):
        return f"{self.text[:50]}..."


class SubjectPerformance(models.Model):
    """Model for tracking subject performance"""
    subject = models.CharField(max_length=100, unique=True)
    grade = models.CharField(max_length=5)
    percentage = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-percentage']

    def __str__(self):
        return f"{self.subject}: {self.grade} ({self.percentage}%)"


class Exam(models.Model):
    """Model for upcoming exams"""
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    exam_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['exam_date']

    def __str__(self):
        return f"{self.title} - {self.subject}"

    @property
    def days_until(self):
        """Calculate days until the exam"""
        delta = self.exam_date - timezone.now().date()
        return max(0, delta.days)
