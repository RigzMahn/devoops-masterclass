from django.core.management.base import BaseCommand

from courses.models import Technology, WorkflowDiagram


class Command(BaseCommand):
    help = 'Populate workflow diagrams for DevOps technologies'

    def handle(self, *args, **options):
        self.stdout.write('Creating workflow diagrams...')
        
        workflow_data = {
            'Git': {
                'title': 'Git Basic Workflow',
                'description': 'Standard Git workflow for version control',
                'diagram_data': """
graph TD
    A[Working Directory] --> B[Staging Area git add]
    B --> C[Local Repository git commit]
    C --> D[Remote Repository git push]
    D --> A
    
    E[Remote Changes] --> F[Local Repository git pull/fetch]
    F --> A
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#f3e5f5
                """,
                'order': 1
            },
            'GitHub': {
                'title': 'GitHub Collaboration Flow',
                'description': 'Standard GitHub workflow for team collaboration',
                'diagram_data': """
graph TB
    A[Fork Repository] --> B[Clone Locally]
    B --> C[Create Feature Branch]
    C --> D[Make Changes & Commit]
    D --> E[Push to Fork]
    E --> F[Create Pull Request]
    F --> G[Code Review]
    G --> H[Merge to Main]
    H --> I[Sync Fork]
    
    style A fill:#e1f5fe
    style F fill:#fff3e0
    style G fill:#e8f5e8
    style H fill:#f3e5f5
                """,
                'order': 1
            },
            'Docker': {
                'title': 'Docker Container Lifecycle',
                'description': 'Complete Docker container management workflow',
                'diagram_data': """
graph LR
    A[Dockerfile] --> B[Build Image docker build]
    B --> C[Tag Image docker tag]
    C --> D[Push to Registry docker push]
    D --> E[Pull Image docker pull]
    E --> F[Run Container docker run]
    F --> G[Manage Container docker start/stop]
    G --> H[Monitor docker logs/stats]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style F fill:#e8f5e8
    style H fill:#fff3e0
                """,
                'order': 1
            },
            'Kubernetes': {
                'title': 'Kubernetes Deployment Flow',
                'description': 'Application deployment workflow in Kubernetes',
                'diagram_data': """
graph TB
    A[Write Application Code] --> B[Create Docker Image]
    B --> C[Push to Container Registry]
    C --> D[Define K8s Manifests]
    D --> E[Apply Configuration kubectl apply]
    E --> F[K8s Creates Pods]
    F --> G[Service Load Balancer]
    G --> H[External Access]
    
    subgraph Kubernetes Cluster
        F
        G
        I[Deployment]
        J[Service]
        K[ConfigMap]
        L[Secret]
    end
    
    style D fill:#e1f5fe
    style E fill:#f3e5f5
    style F fill:#e8f5e8
    style G fill:#fff3e0
                """,
                'order': 1
            },
            'Terraform': {
                'title': 'Terraform Infrastructure as Code',
                'description': 'Terraform workflow for infrastructure management',
                'diagram_data': """
graph TB
    A[Write Terraform Config] --> B[Initialize terraform init]
    B --> C[Plan Changes terraform plan]
    C --> D[Apply Infrastructure terraform apply]
    D --> E[Infrastructure Created]
    E --> F[Manage State]
    F --> G[Destroy terraform destroy]
    
    style A fill:#e1f5fe
    style C fill:#fff3e0
    style D fill:#e8f5e8
    style G fill:#fce4ec
                """,
                'order': 1
            },
            'GitHub Actions': {
                'title': 'GitHub Actions CI/CD Pipeline',
                'description': 'Complete CI/CD workflow with GitHub Actions',
                'diagram_data': """
graph LR
    A[Code Push/PR] --> B[Trigger Workflow]
    B --> C[Checkout Code]
    C --> D[Setup Environment]
    D --> E[Run Tests]
    E --> F[Build Application]
    F --> G[Security Scan]
    G --> H[Deploy to Staging]
    H --> I[Integration Tests]
    I --> J[Deploy to Production]
    
    style E fill:#fff3e0
    style F fill:#e8f5e8
    style J fill:#f3e5f5
                """,
                'order': 1
            }
        }
        
        for tech_name, workflow_info in workflow_data.items():
            try:
                technology = Technology.objects.get(name=tech_name)
                workflow, created = WorkflowDiagram.objects.get_or_create(
                    technology=technology,
                    title=workflow_info['title'],
                    defaults={
                        'description': workflow_info['description'],
                        'diagram_data': workflow_info['diagram_data'],
                        'order': workflow_info['order']
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✅ Created workflow for {tech_name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Workflow already exists for {tech_name}"))
            except Technology.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Technology not found: {tech_name}"))
        
        self.stdout.write(self.style.SUCCESS('🎉 Workflow diagrams populated successfully!'))