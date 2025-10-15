from django.core.management.base import BaseCommand
from courses.models import Technology, Course, Lesson, InteractiveExercise
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populate interactive exercises for DevOps courses'

    def handle(self, *args, **options):
        self.stdout.write('Creating interactive exercises for DevOps technologies...')
        
        exercise_data = [
            # Git Exercises
            {
                'technology': 'Git',
                'lesson_title': 'Introduction to Git',
                'exercises': [
                    {
                        'title': 'Initialize Git Repository',
                        'exercise_type': 'code',
                        'instructions': """
                        <h3>Initialize a Git Repository</h3>
                        <p>Your task is to initialize a new Git repository in the current directory.</p>
                        <div class="alert alert-info">
                            <strong>Hint:</strong> Use the command that creates a new Git repository.
                        </div>
                        """,
                        'initial_code': '# Write the Git command to initialize a repository\n',
                        'solution_code': 'git init',
                        'points': 10,
                        'order': 1
                    },
                    {
                        'title': 'Stage Files for Commit',
                        'exercise_type': 'code',
                        'instructions': """
                        <h3>Stage Files for Commit</h3>
                        <p>You have modified a file called <code>app.py</code>. Stage this file for the next commit.</p>
                        """,
                        'initial_code': '# Stage the app.py file for commit\n',
                        'solution_code': 'git add app.py',
                        'points': 10,
                        'order': 2
                    },
                    {
                        'title': 'Git Basic Commands Quiz',
                        'exercise_type': 'quiz',
                        'instructions': """
                        <h3>Git Basics Quiz</h3>
                        <p>Test your understanding of fundamental Git commands.</p>
                        """,
                        'options': {
                            'question': 'Which command is used to save your changes to the local repository?',
                            'choices': [
                                {'value': 'A', 'text': 'git save'},
                                {'value': 'B', 'text': 'git commit'},
                                {'value': 'C', 'text': 'git store'},
                                {'value': 'D', 'text': 'git push'}
                            ],
                            'correct_answer': 'B'
                        },
                        'points': 5,
                        'order': 3
                    }
                ]
            },
            {
                'technology': 'Git',
                'lesson_title': 'Git Branching and Merging',
                'exercises': [
                    {
                        'title': 'Create and Switch to New Branch',
                        'exercise_type': 'code',
                        'instructions': """
                        <h3>Create a Feature Branch</h3>
                        <p>Create a new branch called "feature-user-auth" and switch to it immediately.</p>
                        """,
                        'initial_code': '# Create and switch to feature-user-auth branch\n',
                        'solution_code': 'git checkout -b feature-user-auth',
                        'points': 15,
                        'order': 1
                    },
                    {
                        'title': 'Merge Branches',
                        'exercise_type': 'quiz',
                        'instructions': """
                        <h3>Branch Merging Strategy</h3>
                        <p>What is the recommended approach for merging feature branches?</p>
                        """,
                        'options': {
                            'question': 'Which merging strategy creates a new commit that ties together the histories?',
                            'choices': [
                                {'value': 'A', 'text': 'Fast-forward merge'},
                                {'value': 'B', 'text': 'Squash merge'},
                                {'value': 'C', 'text': 'Merge commit'},
                                {'value': 'D', 'text': 'Rebase'}
                            ],
                            'correct_answer': 'C'
                        },
                        'points': 10,
                        'order': 2
                    }
                ]
            },
            
            # Docker Exercises
            {
                'technology': 'Docker',
                'lesson_title': 'Docker Basics',
                'exercises': [
                    {
                        'title': 'Create Basic Dockerfile',
                        'exercise_type': 'code',
                        'instructions': """
                        <h3>Build a Python Docker Image</h3>
                        <p>Create a Dockerfile that:</p>
                        <ul>
                            <li>Uses the <code>python:3.11-slim</code> base image</li>
                            <li>Sets the working directory to <code>/app</code></li>
                            <li>Copies the current directory to the container</li>
                            <li>Runs <code>pip install -r requirements.txt</code></li>
                        </ul>
                        """,
                        'initial_code': '# Write your Dockerfile here\n',
                        'solution_code': """FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt""",
                        'points': 20,
                        'order': 1
                    },
                    {
                        'title': 'Docker Commands Quiz',
                        'exercise_type': 'quiz',
                        'instructions': """
                        <h3>Docker Commands Knowledge Check</h3>
                        <p>Test your understanding of essential Docker commands.</p>
                        """,
                        'options': {
                            'question': 'Which command builds a Docker image from a Dockerfile?',
                            'choices': [
                                {'value': 'A', 'text': 'docker create'},
                                {'value': 'B', 'text': 'docker build'},
                                {'value': 'C', 'text': 'docker run'},
                                {'value': 'D', 'text': 'docker compose'}
                            ],
                            'correct_answer': 'B'
                        },
                        'points': 8,
                        'order': 2
                    }
                ]
            },
            
            # GitHub Exercises
            {
                'technology': 'GitHub',
                'lesson_title': 'GitHub Workflows',
                'exercises': [
                    {
                        'title': 'GitHub Collaboration Quiz',
                        'exercise_type': 'quiz',
                        'instructions': """
                        <h3>GitHub Collaboration Patterns</h3>
                        <p>Understand the standard GitHub workflow for team collaboration.</p>
                        """,
                        'options': {
                            'question': 'What is the recommended way to contribute to an open-source project on GitHub?',
                            'choices': [
                                {'value': 'A', 'text': 'Directly push to the main branch'},
                                {'value': 'B', 'text': 'Fork the repository and create a pull request'},
                                {'value': 'C', 'text': 'Create an issue and wait for maintainers'},
                                {'value': 'D', 'text': 'Clone and make changes locally without pushing'}
                            ],
                            'correct_answer': 'B'
                        },
                        'points': 12,
                        'order': 1
                    }
                ]
            },
            
            # Kubernetes Exercises
            {
                'technology': 'Kubernetes',
                'lesson_title': 'Kubernetes Basics',
                'exercises': [
                    {
                        'title': 'Basic Pod Configuration',
                        'exercise_type': 'code',
                        'instructions': """
                        <h3>Create a Simple Pod</h3>
                        <p>Write a basic Pod manifest that:</p>
                        <ul>
                            <li>Has the name "web-app-pod"</li>
                            <li>Uses the nginx:alpine image</li>
                            <li>Exposes port 80</li>
                        </ul>
                        """,
                        'initial_code': """apiVersion: v1
kind: Pod
metadata:
  name: 
spec:
  containers:
  - name: 
    image: 
    ports:
    - containerPort: """,
                        'solution_code': """apiVersion: v1
kind: Pod
metadata:
  name: web-app-pod
spec:
  containers:
  - name: nginx-container
    image: nginx:alpine
    ports:
    - containerPort: 80""",
                        'points': 25,
                        'order': 1
                    }
                ]
            },
            
            # Terraform Exercises
            {
                'technology': 'Terraform',
                'lesson_title': 'Terraform Fundamentals',
                'exercises': [
                    {
                        'title': 'Terraform Workflow Quiz',
                        'exercise_type': 'quiz',
                        'instructions': """
                        <h3>Terraform Command Order</h3>
                        <p>What is the correct order of Terraform commands when deploying infrastructure?</p>
                        """,
                        'options': {
                            'question': 'Which sequence represents the standard Terraform workflow?',
                            'choices': [
                                {'value': 'A', 'text': 'apply → plan → init'},
                                {'value': 'B', 'text': 'init → plan → apply'},
                                {'value': 'C', 'text': 'plan → apply → init'},
                                {'value': 'D', 'text': 'init → apply → plan'}
                            ],
                            'correct_answer': 'B'
                        },
                        'points': 10,
                        'order': 1
                    }
                ]
            },
            
            # Jenkins Exercises
            {
                'technology': 'Jenkins',
                'lesson_title': 'Jenkins Pipeline Basics',
                'exercises': [
                    {
                        'title': 'Jenkinsfile Structure',
                        'exercise_type': 'code',
                        'instructions': """
                        <h3>Create a Basic Jenkins Pipeline</h3>
                        <p>Write a simple Jenkinsfile that defines a pipeline with one stage called "Build".</p>
                        """,
                        'initial_code': """pipeline {
    agent any
    stages {
        // Add your stage here
    }
}""",
                        'solution_code': """pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building the application...'
            }
        }
    }
}""",
                        'points': 15,
                        'order': 1
                    }
                ]
            }
        ]
        
        exercises_created = 0
        
        for tech_exercise in exercise_data:
            try:
                technology = Technology.objects.get(name=tech_exercise['technology'])
                course = Course.objects.get(technology=technology)
                
                # Find the lesson by title or create one
                lesson = Lesson.objects.filter(
                    module__course=course,
                    title__icontains=tech_exercise['lesson_title']
                ).first()
                
                if not lesson:
                    # Create a lesson if it doesn't exist
                    module = course.modules.first()
                    if not module:
                        module = course.modules.create(
                            title=f"{technology.name} Fundamentals",
                            description=f"Learn the basics of {technology.name}",
                            order=1
                        )
                    
                    lesson = Lesson.objects.create(
                        module=module,
                        title=tech_exercise['lesson_title'],
                        content=f"<h2>{tech_exercise['lesson_title']}</h2><p>Learn about {technology.name} through interactive exercises.</p>",
                        lesson_type='practice',
                        order=1,
                        duration_minutes=30,
                        is_free=True
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Created lesson: {lesson.title}"))
                
                for exercise_info in tech_exercise['exercises']:
                    exercise, created = InteractiveExercise.objects.get_or_create(
                        lesson=lesson,
                        title=exercise_info['title'],
                        defaults={
                            'exercise_type': exercise_info['exercise_type'],
                            'instructions': exercise_info['instructions'],
                            'initial_code': exercise_info.get('initial_code', ''),
                            'solution_code': exercise_info.get('solution_code', ''),
                            'options': exercise_info.get('options'),
                            'points': exercise_info['points'],
                            'order': exercise_info['order']
                        }
                    )
                    
                    if created:
                        exercises_created += 1
                        self.stdout.write(self.style.SUCCESS(f"✅ Created exercise: {exercise.title}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠️ Exercise already exists: {exercise.title}"))
                        
            except Technology.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Technology not found: {tech_exercise['technology']}"))
            except Course.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Course not found for: {tech_exercise['technology']}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error creating exercises for {tech_exercise['technology']}: {str(e)}"))
        
        self.stdout.write(
            self.style.SUCCESS(f'🎉 Successfully created {exercises_created} interactive exercises!')
        )
        
        # Summary
        total_exercises = InteractiveExercise.objects.count()
        total_lessons_with_exercises = Lesson.objects.filter(interactive_exercises__isnull=False).distinct().count()
        
        self.stdout.write(self.style.SUCCESS(f'📊 Total exercises in database: {total_exercises}'))
        self.stdout.write(self.style.SUCCESS(f'📚 Lessons with exercises: {total_lessons_with_exercises}'))