from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api.models import (
    ScheduleItem, Quiz, QuizQuestion, Assignment,
    WeeklyGoal, StudyActivity, SubjectPerformance, Exam
)


class Command(BaseCommand):
    help = 'Seeds the database with sample data (only if empty)'

    def handle(self, *args, **options):
        # Check if data already exists - if so, skip seeding
        if ScheduleItem.objects.exists() or Quiz.objects.exists():
            self.stdout.write(self.style.SUCCESS('Database already has data. Skipping seed.'))
            return
        
        self.stdout.write('Seeding database with initial data...')
        
        today = timezone.now().date()
        
        # Create Schedule Items for today
        schedule_data = [
            {'start_time': '09:00', 'end_time': '10:30', 'subject': 'Mathematics - Calculus II', 'status': 'upcoming'},
            {'start_time': '11:00', 'end_time': '12:30', 'subject': 'Computer Science - Data Structures', 'status': 'upcoming'},
            {'start_time': '14:00', 'end_time': '15:30', 'subject': 'Physics - Mechanics', 'status': 'upcoming'},
        ]
        for item in schedule_data:
            ScheduleItem.objects.create(date=today, **item)
        self.stdout.write(f'  Created {len(schedule_data)} schedule items')
        
        # Create Quiz with Questions
        quiz = Quiz.objects.create(
            title='Mathematics Quiz',
            subject='Mathematics',
            topic='Derivatives',
            quiz_date=today + timedelta(days=2),
            time_limit=15
        )
        
        questions = [
            {
                'question_text': 'What is the derivative of x²?',
                'option_a': 'x', 'option_b': '2x', 'option_c': 'x²', 'option_d': '2',
                'correct_answer': 1,
                'explanation': 'Using the power rule: d/dx(x²) = 2x¹ = 2x',
                'order': 0
            },
            {
                'question_text': 'What is the derivative of sin(x)?',
                'option_a': 'cos(x)', 'option_b': '-cos(x)', 'option_c': 'sin(x)', 'option_d': '-sin(x)',
                'correct_answer': 0,
                'explanation': 'The derivative of sin(x) is cos(x)',
                'order': 1
            },
            {
                'question_text': 'What is the derivative of e^x?',
                'option_a': 'e^x', 'option_b': 'xe^(x-1)', 'option_c': 'ln(x)', 'option_d': '1/x',
                'correct_answer': 0,
                'explanation': 'The derivative of e^x is e^x itself',
                'order': 2
            },
            {
                'question_text': 'Using the chain rule, what is the derivative of (2x + 1)³?',
                'option_a': '6(2x + 1)²', 'option_b': '3(2x + 1)²', 'option_c': '(2x + 1)²', 'option_d': '6(2x + 1)',
                'correct_answer': 0,
                'explanation': 'Using chain rule: d/dx[(2x + 1)³] = 3(2x + 1)² × 2 = 6(2x + 1)²',
                'order': 3
            },
            {
                'question_text': 'What is the derivative of ln(x)?',
                'option_a': '1/x', 'option_b': 'x', 'option_c': 'ln(x)', 'option_d': 'e^x',
                'correct_answer': 0,
                'explanation': 'The derivative of ln(x) is 1/x',
                'order': 4
            },
        ]
        for q in questions:
            QuizQuestion.objects.create(quiz=quiz, **q)
        self.stdout.write(f'  Created quiz with {len(questions)} questions')
        
        # Create Exam
        Exam.objects.all().delete()
        Exam.objects.create(
            title='Midterm Exam',
            subject='Physics - Mechanics',
            exam_date=today + timedelta(days=5)
        )
        self.stdout.write('  Created exam')
        
        # Create Assignments
        Assignment.objects.all().delete()
        assignments = [
            {'title': 'Calculus Problem Set 5', 'subject': 'Mathematics', 'due_date': today + timedelta(days=3), 'status': 'completed'},
            {'title': 'Data Structures Project', 'subject': 'Computer Science', 'due_date': today + timedelta(days=5), 'status': 'completed'},
            {'title': 'Physics Lab Report', 'subject': 'Physics', 'due_date': today + timedelta(days=7), 'status': 'in-progress'},
            {'title': 'Algorithm Analysis', 'subject': 'Computer Science', 'due_date': today + timedelta(days=10), 'status': 'pending'},
        ]
        for a in assignments:
            Assignment.objects.create(**a)
        self.stdout.write(f'  Created {len(assignments)} assignments')
        
        # Create Weekly Goals
        week_start = today - timedelta(days=today.weekday())
        WeeklyGoal.objects.all().delete()
        goals = [
            {'text': 'Complete 3 practice problems for Calculus', 'status': 'completed', 'week_start': week_start},
            {'text': 'Finish reading Chapter 7 - Biology', 'status': 'in-progress', 'week_start': week_start},
            {'text': 'Start preparing for History midterm', 'status': 'pending', 'week_start': week_start},
        ]
        for g in goals:
            WeeklyGoal.objects.create(**g)
        self.stdout.write(f'  Created {len(goals)} weekly goals')
        
        # Create Study Activities
        StudyActivity.objects.all().delete()
        activities = [
            {'text': 'Completed Chapter 5 Notes - Linear Algebra', 'activity_time': timezone.now() - timedelta(minutes=30)},
            {'text': 'Submitted Assignment - Data Structures Project', 'activity_time': timezone.now() - timedelta(hours=2)},
            {'text': 'Reviewed for upcoming Physics exam', 'activity_time': timezone.now() - timedelta(days=1)},
        ]
        for a in activities:
            StudyActivity.objects.create(**a)
        self.stdout.write(f'  Created {len(activities)} study activities')
        
        # Create Subject Performance
        SubjectPerformance.objects.all().delete()
        subjects = [
            {'subject': 'Mathematics', 'grade': 'A-', 'percentage': 85},
            {'subject': 'Computer Science', 'grade': 'A', 'percentage': 92},
            {'subject': 'Physics', 'grade': 'B+', 'percentage': 78},
        ]
        for s in subjects:
            SubjectPerformance.objects.create(**s)
        self.stdout.write(f'  Created {len(subjects)} subject performance records')
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
