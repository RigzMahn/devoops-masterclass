from django.core.management.base import BaseCommand

from courses.models import (
    CodeExample,
    Course,
    Lesson,
    Module,
    Technology,
    WorkflowDiagram,
)


class Command(BaseCommand):
    help = 'Populate database with comprehensive DevOps technologies and courses'

    def handle(self, *args, **options):
        self.stdout.write('Creating comprehensive DevOps learning data...')
        
        technologies_data = [
            # Phase 1: Version Control & Collaboration
            {
                'name': 'Git',
                'category': 'vcs',
                'phase': 1,
                'order': 1,
                'description': 'Distributed version control system for tracking changes in source code during software development.',
                'official_docs_url': 'https://git-scm.com/doc'
            },
            {
                'name': 'GitHub',
                'category': 'vcs', 
                'phase': 1,
                'order': 2,
                'description': 'Web-based platform for version control and collaboration using Git. Provides hosting for software development.',
                'official_docs_url': 'https://docs.github.com'
            },
            {
                'name': 'GitLab',
                'category': 'vcs',
                'phase': 1, 
                'order': 3,
                'description': 'Complete DevOps platform with integrated version control, CI/CD, issue tracking, and collaboration features.',
                'official_docs_url': 'https://docs.gitlab.com'
            },

            # Phase 2: CI/CD Automation
            {
                'name': 'GitHub Actions',
                'category': 'ci_cd',
                'phase': 2,
                'order': 1,
                'description': 'Automate software workflows with CI/CD directly in your GitHub repository. Native integration with GitHub ecosystem.',
                'official_docs_url': 'https://docs.github.com/en/actions'
            },
            {
                'name': 'Jenkins',
                'category': 'ci_cd',
                'phase': 2,
                'order': 2,
                'description': 'Open-source automation server for building, testing, and deploying. Highly extensible with plugins.',
                'official_docs_url': 'https://www.jenkins.io/doc/'
            },
            {
                'name': 'CircleCI',
                'category': 'ci_cd',
                'phase': 2,
                'order': 3,
                'description': 'Continuous integration and delivery platform for rapid software development with cloud and self-hosted options.',
                'official_docs_url': 'https://circleci.com/docs/'
            },

            # Phase 3: Containerization & Orchestration
            {
                'name': 'Docker',
                'category': 'container',
                'phase': 3,
                'order': 1,
                'description': 'Platform for developing, shipping, and running applications in containers. Standard for containerization.',
                'official_docs_url': 'https://docs.docker.com/'
            },
            {
                'name': 'Kubernetes',
                'category': 'orchestration',
                'phase': 3,
                'order': 2,
                'description': 'Container orchestration system for automating deployment, scaling, and management of containerized applications.',
                'official_docs_url': 'https://kubernetes.io/docs/'
            },

            # Phase 4: Infrastructure as Code
            {
                'name': 'Terraform',
                'category': 'iac',
                'phase': 4,
                'order': 1,
                'description': 'Infrastructure as Code tool for building, changing, and versioning infrastructure safely and efficiently.',
                'official_docs_url': 'https://www.terraform.io/docs/'
            },
            {
                'name': 'Ansible',
                'category': 'iac',
                'phase': 4,
                'order': 2,
                'description': 'Configuration management and application deployment tool using simple YAML playbooks. Agentless architecture.',
                'official_docs_url': 'https://docs.ansible.com/'
            },

            # Phase 5: Monitoring & Observability
            {
                'name': 'Prometheus',
                'category': 'monitoring',
                'phase': 5,
                'order': 1,
                'description': 'Open-source monitoring and alerting toolkit designed for reliability and scalability. Time-series database.',
                'official_docs_url': 'https://prometheus.io/docs/'
            },
            {
                'name': 'Grafana',
                'category': 'monitoring',
                'phase': 5,
                'order': 2,
                'description': 'Open-source platform for monitoring and observability with beautiful dashboards and data visualization.',
                'official_docs_url': 'https://grafana.com/docs/'
            },
            {
                'name': 'ELK Stack',
                'category': 'monitoring',
                'phase': 5,
                'order': 3,
                'description': 'Elasticsearch, Logstash, and Kibana stack for log analysis, search, and visualization at scale.',
                'official_docs_url': 'https://www.elastic.co/guide/index.html'
            },

            # Phase 6: Security & Quality
            {
                'name': 'SonarQube',
                'category': 'security',
                'phase': 6,
                'order': 1,
                'description': 'Platform for continuous inspection of code quality to perform automatic reviews and detect bugs and vulnerabilities.',
                'official_docs_url': 'https://docs.sonarqube.org/'
            },
            {
                'name': 'HashiCorp Vault',
                'category': 'security',
                'phase': 6,
                'order': 2,
                'description': 'Tool for secrets management, data encryption, and identity-based access control in modern applications.',
                'official_docs_url': 'https://www.vaultproject.io/docs'
            }
        ]

        for tech_data in technologies_data:
            tech, created = Technology.objects.get_or_create(
                name=tech_data['name'],
                defaults=tech_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created technology: {tech.name}"))
                
                # Create a comprehensive course for each technology
                course = Course.objects.create(
                    technology=tech,
                    title=f"Complete {tech.name} Mastery",
                    description=f"Comprehensive course covering {tech.name} from fundamentals to advanced implementation. Learn best practices and real-world applications.",
                    difficulty='intermediate' if tech.phase <= 3 else 'advanced',
                    estimated_duration=10 if tech.phase <= 2 else 8,
                    is_active=True
                )
                
                # Create detailed modules based on technology phase
                if tech.phase == 1:  # Version Control
                    modules_data = [
                        {'title': 'Fundamentals & Core Concepts', 'order': 1, 'description': 'Learn the basic concepts and workflow'},
                        {'title': 'Advanced Features & Techniques', 'order': 2, 'description': 'Master advanced capabilities and optimizations'},
                        {'title': 'Team Collaboration & Workflows', 'order': 3, 'description': 'Implement effective team collaboration strategies'},
                        {'title': 'Real-world Projects & Best Practices', 'order': 4, 'description': 'Apply knowledge to real scenarios'},
                    ]
                elif tech.phase == 2:  # CI/CD
                    modules_data = [
                        {'title': 'CI/CD Concepts & Pipeline Design', 'order': 1, 'description': 'Understand continuous integration and delivery principles'},
                        {'title': 'Configuration & Setup', 'order': 2, 'description': 'Configure and set up automation pipelines'},
                        {'title': 'Advanced Pipeline Features', 'order': 3, 'description': 'Implement complex workflows and integrations'},
                        {'title': 'Monitoring & Optimization', 'order': 4, 'description': 'Monitor pipeline performance and optimize workflows'},
                    ]
                else:  # Other phases
                    modules_data = [
                        {'title': 'Introduction & Core Concepts', 'order': 1, 'description': 'Understand fundamental concepts and architecture'},
                        {'title': 'Implementation & Configuration', 'order': 2, 'description': 'Hands-on implementation and configuration'},
                        {'title': 'Advanced Features & Integration', 'order': 3, 'description': 'Master advanced capabilities and ecosystem integration'},
                        {'title': 'Production Deployment & Best Practices', 'order': 4, 'description': 'Deploy to production and follow best practices'},
                    ]
                
                for module_data in modules_data:
                    module = Module.objects.create(
                        course=course,
                        title=module_data['title'],
                        description=module_data['description'],
                        order=module_data['order']
                    )
                    
                    # Create sample lessons with rich content
                    lesson_content = f"""
                    <h2>Welcome to {tech.name}</h2>
                    <p>This lesson introduces you to the fundamental concepts of {tech.name} and its importance in modern DevOps practices.</p>
                    
                    <h3>Key Learning Objectives</h3>
                    <ul>
                        <li>Understand the core concepts of {tech.name}</li>
                        <li>Learn the basic workflow and commands</li>
                        <li>Set up your development environment</li>
                        <li>Complete your first practical exercise</li>
                    </ul>
                    
                    <div class="alert alert-info">
                        <strong>Pro Tip:</strong> Practice regularly and don't hesitate to experiment with different scenarios.
                    </div>
                    """
                    
                    lesson = Lesson.objects.create(
                        module=module,
                        title=f'Introduction to {tech.name}',
                        content=lesson_content,
                        lesson_type='theory',
                        order=1,
                        duration_minutes=45,
                        is_free=True
                    )
                    
                    # Add a code example for the lesson
                    if tech.name == 'Git':
                        code_example = CodeExample.objects.create(
                            lesson=lesson,
                            title='Basic Git Commands',
                            description='Essential Git commands for version control',
                            code="""# Initialize a new Git repository
git init

# Check the status of your repository
git status

# Add files to staging area
git add filename.py
git add .  # Add all files

# Commit changes with a message
git commit -m "Initial commit"

# View commit history
git log --oneline""",
                            language='bash',
                            explanation="""
                            <h4>Understanding Basic Git Workflow</h4>
                            <p>These commands represent the fundamental Git workflow:</p>
                            <ol>
                                <li><code>git init</code> - Creates a new Git repository</li>
                                <li><code>git status</code> - Shows the current state of your repository</li>
                                <li><code>git add</code> - Stages changes for commit</li>
                                <li><code>git commit</code> - Saves changes to the repository history</li>
                                <li><code>git log</code> - Displays the commit history</li>
                            </ol>
                            """,
                            order=1
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Successfully created {Technology.objects.count()} technologies with comprehensive courses!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'📚 Total courses: {Course.objects.count()}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'📖 Total lessons: {Lesson.objects.count()}'
            )
        )