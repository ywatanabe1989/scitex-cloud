from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import random
import json
from apps.document_app.models import Document
from apps.auth_app.models import UserProfile
from apps.project_app.models import Project
from .directory_manager import get_user_directory_manager


def generate_smart_recommendations(user):
    """Generate personalized recommendations based on user activity."""
    recommendations = []
    
    # Get user's project count
    project_count = Project.objects.filter(owner=user).count()
    
    # Get user's registration date
    days_since_registration = (datetime.now().date() - user.date_joined.date()).days
    
    # Smart recommendations based on user state
    if project_count == 0:
        recommendations.append({
            'type': 'action',
            'title': 'Create Your First Project',
            'description': 'Start organizing your research with a dedicated project workspace',
            'action_url': '/core/project-list/',
            'icon': 'fas fa-plus-circle',
            'priority': 'high'
        })
    
    if days_since_registration <= 7:
        recommendations.append({
            'type': 'explore',
            'title': 'Discover SciTeX Scholar',
            'description': 'Search through millions of scientific papers with our advanced semantic search',
            'action_url': '/scholar/',
            'icon': 'fas fa-search',
            'priority': 'medium'
        })
        
        recommendations.append({
            'type': 'learn',
            'title': 'Try LaTeX Writing',
            'description': 'Write and compile scientific documents with our integrated LaTeX editor',
            'action_url': '/writer/',
            'icon': 'fas fa-edit',
            'priority': 'medium'
        })
    
    # Add productivity tips for active users
    if project_count > 0:
        recommendations.append({
            'type': 'tip',
            'title': 'Pro Tip: Use Keywords',
            'description': 'Add keywords to your projects for better organization and search',
            'action_url': None,
            'icon': 'fas fa-lightbulb',
            'priority': 'low'
        })
    
    return recommendations[:3]  # Limit to 3 recommendations


def landing(request):
    """Landing page view."""
    return render(request, 'core_app/landing.html')


@login_required
def index(request):
    """Dashboard/index view - Redirect to Projects."""
    # Dashboard is just the projects/file manager - redirect directly to GitHub-style URLs
    return redirect('/projects/')


@login_required
def dashboard_react_tree(request):
    """File Manager Dashboard - Single page with file browser only."""
    user = request.user
    
    context = {
        'user': user,
    }
    
    return render(request, 'core_app/dashboard_react_tree.html', context)


def about(request):
    """About page view."""
    return render(request, 'core_app/about.html')


def contact(request):
    """Contact page view."""
    return render(request, 'core_app/contact.html')


def privacy_policy(request):
    """Privacy policy page view."""
    return render(request, 'core_app/privacy_policy.html')


def terms_of_use(request):
    """Terms of use page view."""
    return render(request, 'core_app/terms_of_use.html')


def cookie_policy(request):
    """Cookie policy page view."""
    return render(request, 'core_app/cookie_policy.html')


@login_required
def document_list(request):
    """Document list view."""
    documents = Document.objects.filter(owner=request.user).order_by('-updated_at')
    
    # Filter by document type if specified
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        documents = documents.filter(title__icontains=search_query)
    
    context = {
        'documents': documents,
        'search_query': search_query,
        'selected_type': doc_type,
        'document_types': Document.DOCUMENT_TYPES,
    }
    
    return render(request, 'core_app/document_list.html', context)


@login_required
def project_list(request):
    """Project list view."""
    projects = Project.objects.filter(owner=request.user).order_by('-updated_at')
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        projects = projects.filter(status=status)
    
    # Check if user has any projects
    has_projects = projects.exists()
    
    context = {
        'projects': projects,
        'selected_status': status,
        'project_statuses': Project.PROJECT_STATUS,
        'has_projects': has_projects,
    }
    
    return render(request, 'core_app/project_list.html', context)


@login_required
def profile_view(request):
    """User profile view."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'profile': profile,
    }
    
    return render(request, 'core_app/profile.html', context)


@login_required
def monitoring(request):
    """Display the real-time monitoring dashboard."""
    User = get_user_model()
    
    # Calculate metrics
    active_users = User.objects.filter(
        last_login__gte=datetime.now() - timedelta(minutes=30)
    ).count()
    
    # Mock data for demonstration
    context = {
        'active_users': active_users,
        'api_requests': random.randint(1000, 5000),
        'cpu_usage': random.randint(20, 80),
        'memory_usage': random.randint(30, 70),
        'storage_used': random.randint(40, 60),
        'services': {
            'web_server': 'operational',
            'database': 'operational',
            'storage': 'operational',
            'redis_cache': 'operational'
        }
    }
    
    return render(request, 'core_app/monitoring.html', context)


@login_required
def monitoring_data(request):
    """API endpoint for real-time monitoring data."""
    if request.method == 'GET':
        # Generate mock data for demonstration
        data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'active_users': random.randint(50, 200),
                'api_requests': random.randint(1000, 5000),
                'cpu_usage': random.randint(20, 80),
                'memory_usage': random.randint(30, 70),
                'network_in': random.randint(100, 500),
                'network_out': random.randint(100, 500)
            },
            'services': {
                'web_server': 'operational',
                'database': 'operational',
                'storage': 'operational',
                'redis_cache': 'operational'
            },
            'recent_activity': [
                {
                    'timestamp': (datetime.now() - timedelta(minutes=i)).strftime('%H:%M:%S'),
                    'event': random.choice([
                        'User login',
                        'API request processed',
                        'File uploaded',
                        'Compilation completed',
                        'Search query executed'
                    ]),
                    'details': f'User {random.randint(100, 999)}'
                }
                for i in range(5)
            ]
        }
        return JsonResponse(data)


@login_required
def create_example_project(request):
    """Create an example project with SCITEX structure."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_type = data.get('type', 'mnist')
            
            # Define example project templates
            example_projects = {
                'mnist': {
                    'name': 'MNIST Digit Classification Example',
                    'description': 'Example project demonstrating machine learning workflow with MNIST digit classification using scikit-learn.',
                    'hypotheses': 'Support Vector Machine (SVM) can achieve >95% accuracy on MNIST digit classification task.',
                    'status': 'planning'
                },
                'data_analysis': {
                    'name': 'Scientific Data Analysis Template',
                    'description': 'Template project for scientific data analysis with data preprocessing, statistical analysis, and visualization.',
                    'hypotheses': 'Template project for defining research hypotheses and conducting systematic data analysis.',
                    'status': 'planning'
                },
                'research_paper': {
                    'name': 'Research Paper Project Template',
                    'description': 'Complete template for academic research project including literature review, methodology, and manuscript preparation.',
                    'hypotheses': 'Define your research hypotheses here based on literature review and gap analysis.',
                    'status': 'planning'
                },
                'scitex_default': {
                    'name': 'SciTeX Default Project',
                    'description': 'Standard SCITEX project structure copied from example-python-project-scitex template.',
                    'hypotheses': 'Define your research hypotheses following the SCITEX framework for reproducible research.',
                    'status': 'planning'
                }
            }
            
            if project_type not in example_projects:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Unknown project type: {project_type}'
                }, status=400)
            
            template = example_projects[project_type]
            
            # Create project with template data
            project = Project.objects.create(
                name=template['name'],
                description=template['description'],
                hypotheses=template['hypotheses'],
                status=template['status'],
                owner=request.user
            )
            
            # Initialize project directory with SCITEX structure
            manager = get_user_directory_manager(request.user)
            success, project_path = manager.create_project_directory(project)
            
            if success:
                # Create example files based on project type
                if project_type == 'scitex_default':
                    _create_scitex_default_project(project_path)
                else:
                    _create_example_files(manager, project, project_path, project_type)
                
                project.directory_created = True
                project.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Example project "{template["name"]}" created successfully',
                    'project_id': project.id,
                    'project_name': project.name,
                    'project_path': project.data_location
                })
            else:
                # Clean up project if directory creation failed
                project.delete()
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to create project directory'
                }, status=500)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error creating example project: {str(e)}'
            }, status=500)
    
    # GET request - return available example projects
    example_types = [
        {
            'type': 'mnist',
            'name': 'MNIST Digit Classification',
            'description': 'Machine learning project with SVM classification',
            'features': ['Data preprocessing', 'Model training', 'Evaluation metrics', 'Visualization']
        },
        {
            'type': 'data_analysis',
            'name': 'Scientific Data Analysis',
            'description': 'Statistical analysis and visualization template',
            'features': ['Data cleaning', 'Statistical tests', 'Plots and charts', 'Report generation']
        },
        {
            'type': 'research_paper',
            'name': 'Research Paper Project',
            'description': 'Complete academic research workflow',
            'features': ['Literature review', 'Methodology', 'Results analysis', 'Manuscript writing']
        },
        {
            'type': 'scitex_default',
            'name': 'SciTeX Default Project',
            'description': 'Standard SCITEX framework template',
            'features': ['Standard structure', 'Example scripts', 'Configuration files', 'Documentation template']
        }
    ]
    
    return JsonResponse({
        'status': 'success',
        'example_projects': example_types
    })


@login_required
def copy_project(request, project_id):
    """Copy an existing project with its structure."""
    if request.method == 'POST':
        try:
            source_project = Project.objects.get(id=project_id, owner=request.user)
            data = json.loads(request.body)
            new_name = data.get('name', f'{source_project.name} (Copy)')
            
            # Create new project with copied data
            new_project = Project.objects.create(
                name=new_name,
                description=source_project.description,
                hypotheses=source_project.hypotheses,
                status='planning',  # Reset status for copy
                owner=request.user
            )
            
            # Copy directory structure
            manager = get_user_directory_manager(request.user)
            success, new_project_path = manager.create_project_directory(new_project)
            
            if success:
                # Copy files from source project if it has a directory
                source_path = manager.get_project_path(source_project)
                if source_path and source_path.exists():
                    _copy_project_files(source_path, new_project_path)
                
                new_project.directory_created = True
                new_project.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Project copied successfully as "{new_name}"',
                    'project_id': new_project.id,
                    'project_name': new_project.name
                })
            else:
                # Clean up if directory creation failed
                new_project.delete()
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to create project directory'
                }, status=500)
                
        except Project.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Source project not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error copying project: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method allowed'
    }, status=405)


def _create_example_files(manager, project, project_path, project_type):
    """Create example files based on project type."""
    try:
        if project_type == 'mnist':
            # Create MNIST example files
            _create_mnist_example_files(project_path)
        elif project_type == 'data_analysis':
            # Create data analysis example files
            _create_data_analysis_example_files(project_path)
        elif project_type == 'research_paper':
            # Create research paper example files
            _create_research_paper_example_files(project_path)
    except Exception as e:
        print(f"Error creating example files: {e}")


def _create_mnist_example_files(project_path):
    """Create MNIST-specific example files."""
    # Create config/MNIST.yaml
    mnist_config = '''# MNIST Classification Configuration
project:
  name: "MNIST Digit Classification"
  version: "1.0"
  description: "SVM-based digit classification on MNIST dataset"

data:
  dataset: "MNIST"
  train_size: 60000
  test_size: 10000
  image_size: [28, 28]
  num_classes: 10

model:
  algorithm: "SVM"
  kernel: "rbf"
  C: 1.0
  gamma: "scale"

training:
  validation_split: 0.2
  random_state: 42
  n_jobs: -1

evaluation:
  metrics: ["accuracy", "precision", "recall", "f1"]
  cross_validation: 5
'''
    
    with open(project_path / 'config' / 'MNIST.yaml', 'w') as f:
        f.write(mnist_config)
    
    # Create example Python script
    mnist_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MNIST Digit Classification Example

This script demonstrates a complete machine learning workflow:
1. Data loading and preprocessing
2. Model training with SVM
3. Evaluation and metrics
4. Visualization of results

Follows SCITEX framework for reproducible research.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import datasets, svm, metrics
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from pathlib import Path
import yaml
import joblib

# Set up paths
project_root = Path(__file__).parent.parent
config_path = project_root / "config" / "MNIST.yaml"
data_path = project_root / "data"
results_path = project_root / "results"

def load_config():
    """Load project configuration."""
    with open(config_path, \'r\') as f:
        return yaml.safe_load(f)

def load_and_preprocess_data():
    """Load and preprocess MNIST data."""
    print("Loading MNIST dataset...")
    
    # Load digits dataset (subset of MNIST)
    digits = datasets.load_digits()
    
    # Flatten images for SVM
    n_samples = len(digits.images)
    X = digits.images.reshape((n_samples, -1))
    y = digits.target
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save preprocessed data
    data_processed_path = data_path / "processed"
    data_processed_path.mkdir(exist_ok=True)
    
    np.save(data_processed_path / "X_train.npy", X_train_scaled)
    np.save(data_processed_path / "X_test.npy", X_test_scaled)
    np.save(data_processed_path / "y_train.npy", y_train)
    np.save(data_processed_path / "y_test.npy", y_test)
    joblib.dump(scaler, data_processed_path / "scaler.pkl")
    
    print(f"Dataset loaded: {X_train.shape} training, {X_test.shape} test")
    return X_train_scaled, X_test_scaled, y_train, y_test, digits

def train_model(X_train, y_train, config):
    """Train SVM model."""
    print("Training SVM model...")
    
    model_config = config[\'model\']
    classifier = svm.SVC(
        kernel=model_config[\'kernel\'],
        C=model_config[\'C\'],
        gamma=model_config[\'gamma\']
    )
    
    classifier.fit(X_train, y_train)
    
    # Save model
    models_path = data_path / "models"
    models_path.mkdir(exist_ok=True)
    joblib.dump(classifier, models_path / "mnist_svm.pkl")
    
    print("Model training completed")
    return classifier

def evaluate_model(classifier, X_test, y_test):
    """Evaluate model performance."""
    print("Evaluating model...")
    
    # Make predictions
    y_pred = classifier.predict(X_test)
    
    # Calculate metrics
    accuracy = metrics.accuracy_score(y_test, y_pred)
    precision = metrics.precision_score(y_test, y_pred, average=\'weighted\')
    recall = metrics.recall_score(y_test, y_pred, average=\'weighted\')
    f1 = metrics.f1_score(y_test, y_pred, average=\'weighted\')
    
    # Confusion matrix
    cm = metrics.confusion_matrix(y_test, y_pred)
    
    # Save results
    results_outputs_path = results_path / "outputs"
    results_outputs_path.mkdir(exist_ok=True)
    
    results_df = pd.DataFrame({
        \'Metric\': [\'Accuracy\', \'Precision\', \'Recall\', \'F1-Score\'],
        \'Value\': [accuracy, precision, recall, f1]
    })
    results_df.to_csv(results_outputs_path / "evaluation_metrics.csv", index=False)
    
    np.save(results_outputs_path / "confusion_matrix.npy", cm)
    np.save(results_outputs_path / "predictions.npy", y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    return {
        \'accuracy\': accuracy,
        \'precision\': precision,
        \'recall\': recall,
        \'f1\': f1,
        \'confusion_matrix\': cm,
        \'predictions\': y_pred
    }

def create_visualizations(digits, y_test, y_pred, cm):
    """Create result visualizations."""
    print("Creating visualizations...")
    
    figures_path = data_path / "figures"
    figures_path.mkdir(exist_ok=True)
    
    # 1. Sample digits visualization
    fig, axes = plt.subplots(2, 5, figsize=(10, 5))
    for i, ax in enumerate(axes.flat):
        ax.imshow(digits.images[i], cmap=\'gray\')
        ax.set_title(f\'Digit: {digits.target[i]}\')
        ax.axis(\'off\')
    plt.suptitle(\'Sample MNIST Digits\')
    plt.tight_layout()
    plt.savefig(figures_path / "sample_digits.png", dpi=300, bbox_inches=\'tight\')
    plt.close()
    
    # 2. Confusion matrix heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt=\'d\', cmap=\'Blues\', 
                xticklabels=range(10), yticklabels=range(10))
    plt.title(\'Confusion Matrix - MNIST SVM Classification\')
    plt.xlabel(\'Predicted Label\')
    plt.ylabel(\'True Label\')
    plt.savefig(figures_path / "confusion_matrix.png", dpi=300, bbox_inches=\'tight\')
    plt.close()
    
    # 3. Classification report visualization
    from sklearn.metrics import classification_report
    report = classification_report(y_test, y_pred, output_dict=True)
    
    # Convert to DataFrame for better visualization
    report_df = pd.DataFrame(report).transpose()
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(report_df.iloc[:-1, :-1], annot=True, cmap=\'RdYlBu\', 
                fmt=\'.3f\', cbar_kws={\'label\': \'Score\'})
    plt.title(\'Classification Report Heatmap\')
    plt.tight_layout()
    plt.savefig(figures_path / "classification_report.png", dpi=300, bbox_inches=\'tight\')
    plt.close()
    
    print("Visualizations saved to data/figures/")

def main():
    """Main execution function."""
    print("=== MNIST Digit Classification Example ===")
    print("Following SCITEX framework for reproducible research\\n")
    
    # Load configuration
    config = load_config()
    print(f"Project: {config[\'project\'][\'name\']}") 
    print(f"Algorithm: {config[\'model\'][\'algorithm\']}") 
    
    # Execute workflow
    X_train, X_test, y_train, y_test, digits = load_and_preprocess_data()
    classifier = train_model(X_train, y_train, config)
    results = evaluate_model(classifier, X_test, y_test)
    create_visualizations(digits, y_test, results[\'predictions\'], results[\'confusion_matrix\'])
    
    print("\\n=== Analysis Complete ===")
    print(f"Final Accuracy: {results[\'accuracy\']:.4f}")
    print("Results saved to results/outputs/")
    print("Figures saved to data/figures/")
    print("Model saved to data/models/")

if __name__ == "__main__":
    main()
'''
    
    with open(project_path / 'scripts' / 'mnist_classification.py', 'w') as f:
        f.write(mnist_script)


def _create_data_analysis_example_files(project_path):
    """Create data analysis example files."""
    # Create example data analysis script
    analysis_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scientific Data Analysis Template

This template demonstrates:
1. Data loading and cleaning
2. Exploratory data analysis
3. Statistical testing
4. Visualization and reporting

Follows SCITEX framework for reproducible research.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path

# Set up paths
project_root = Path(__file__).parent.parent
data_path = project_root / "data"
results_path = project_root / "results"

def load_data():
    """Load and inspect data."""
    print("Loading data...")
    
    # Create example dataset
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        \'group\': np.random.choice([\'A\', \'B\', \'C\'], n_samples),
        \'measurement_1\': np.random.normal(50, 10, n_samples),
        \'measurement_2\': np.random.normal(30, 5, n_samples),
        \'treatment\': np.random.choice([\'Control\', \'Treatment\'], n_samples)
    }
    
    # Add some correlation
    data[\'measurement_2\'] += 0.3 * data[\'measurement_1\'] + np.random.normal(0, 2, n_samples)
    
    df = pd.DataFrame(data)
    
    # Save raw data
    raw_data_path = data_path / "raw"
    raw_data_path.mkdir(exist_ok=True)
    df.to_csv(raw_data_path / "experimental_data.csv", index=False)
    
    print(f"Data loaded: {df.shape}")
    return df

def clean_and_preprocess(df):
    """Clean and preprocess data."""
    print("Cleaning data...")
    
    # Example cleaning steps
    df_clean = df.copy()
    
    # Remove outliers (example: values beyond 3 standard deviations)
    for col in [\'measurement_1\', \'measurement_2\']:
        mean = df_clean[col].mean()
        std = df_clean[col].std()
        df_clean = df_clean[np.abs(df_clean[col] - mean) <= 3 * std]
    
    # Save processed data
    processed_data_path = data_path / "processed"
    processed_data_path.mkdir(exist_ok=True)
    df_clean.to_csv(processed_data_path / "cleaned_data.csv", index=False)
    
    print(f"Data cleaned: {df_clean.shape}")
    return df_clean

def exploratory_analysis(df):
    """Perform exploratory data analysis."""
    print("Performing exploratory analysis...")
    
    # Basic statistics
    summary_stats = df.describe()
    
    # Group analysis
    group_stats = df.groupby(\'group\').agg({
        \'measurement_1\': [\'mean\', \'std\', \'count\'],
        \'measurement_2\': [\'mean\', \'std\', \'count\']
    })
    
    # Save analysis results
    results_outputs_path = results_path / "outputs"
    results_outputs_path.mkdir(exist_ok=True)
    
    summary_stats.to_csv(results_outputs_path / "summary_statistics.csv")
    group_stats.to_csv(results_outputs_path / "group_statistics.csv")
    
    return summary_stats, group_stats

def statistical_tests(df):
    """Perform statistical tests."""
    print("Performing statistical tests...")
    
    results = {}
    
    # T-test between treatment groups
    control = df[df[\'treatment\'] == \'Control\'][\'measurement_1\']
    treatment = df[df[\'treatment\'] == \'Treatment\'][\'measurement_1\']
    
    t_stat, p_value = stats.ttest_ind(control, treatment)
    results[\'t_test\'] = {\'statistic\': t_stat, \'p_value\': p_value}
    
    # ANOVA between groups
    groups = [df[df[\'group\'] == g][\'measurement_1\'] for g in df[\'group\'].unique()]
    f_stat, p_value_anova = stats.f_oneway(*groups)
    results[\'anova\'] = {\'statistic\': f_stat, \'p_value\': p_value_anova}
    
    # Correlation analysis
    correlation = df[[\'measurement_1\', \'measurement_2\']].corr()
    
    # Save results
    results_outputs_path = results_path / "outputs"
    
    with open(results_outputs_path / "statistical_tests.txt", \'w\') as f:
        f.write("Statistical Test Results\\n")
        f.write("======================\\n\\n")
        f.write(f"T-test (Control vs Treatment):\\n")
        f.write(f"  t-statistic: {t_stat:.4f}\\n")
        f.write(f"  p-value: {p_value:.4f}\\n\\n")
        f.write(f"ANOVA (Groups A, B, C):\\n")
        f.write(f"  F-statistic: {f_stat:.4f}\\n")
        f.write(f"  p-value: {p_value_anova:.4f}\\n")
    
    correlation.to_csv(results_outputs_path / "correlation_matrix.csv")
    
    return results

def create_visualizations(df):
    """Create data visualizations."""
    print("Creating visualizations...")
    
    figures_path = data_path / "figures"
    figures_path.mkdir(exist_ok=True)
    
    # Set style
    plt.style.use(\'seaborn-v0_8\')
    
    # 1. Distribution plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Histogram
    axes[0, 0].hist(df[\'measurement_1\'], bins=30, alpha=0.7)
    axes[0, 0].set_title(\'Distribution of Measurement 1\')
    axes[0, 0].set_xlabel(\'Value\')
    axes[0, 0].set_ylabel(\'Frequency\')
    
    # Box plot by group
    df.boxplot(column=\'measurement_1\', by=\'group\', ax=axes[0, 1])
    axes[0, 1].set_title(\'Measurement 1 by Group\')
    
    # Scatter plot
    axes[1, 0].scatter(df[\'measurement_1\'], df[\'measurement_2\'], alpha=0.6)
    axes[1, 0].set_xlabel(\'Measurement 1\')
    axes[1, 0].set_ylabel(\'Measurement 2\')
    axes[1, 0].set_title(\'Correlation Plot\')
    
    # Treatment comparison
    treatment_data = [df[df[\'treatment\'] == t][\'measurement_1\'] for t in df[\'treatment\'].unique()]
    axes[1, 1].boxplot(treatment_data, labels=df[\'treatment\'].unique())
    axes[1, 1].set_title(\'Treatment Comparison\')
    axes[1, 1].set_ylabel(\'Measurement 1\')
    
    plt.tight_layout()
    plt.savefig(figures_path / "data_analysis_plots.png", dpi=300, bbox_inches=\'tight\')
    plt.close()
    
    # 2. Correlation heatmap
    plt.figure(figsize=(8, 6))
    correlation_matrix = df[[\'measurement_1\', \'measurement_2\']].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap=\'coolwarm\', center=0)
    plt.title(\'Correlation Matrix\')
    plt.savefig(figures_path / "correlation_heatmap.png", dpi=300, bbox_inches=\'tight\')
    plt.close()
    
    print("Visualizations saved to data/figures/")

def main():
    """Main analysis pipeline."""
    print("=== Scientific Data Analysis Template ===")
    print("Following SCITEX framework for reproducible research\\n")
    
    # Execute analysis pipeline
    df = load_data()
    df_clean = clean_and_preprocess(df)
    summary_stats, group_stats = exploratory_analysis(df_clean)
    test_results = statistical_tests(df_clean)
    create_visualizations(df_clean)
    
    print("\\n=== Analysis Complete ===")
    print("Results saved to results/outputs/")
    print("Figures saved to data/figures/")
    print("\\nKey Findings:")
    print(f"- Total samples analyzed: {len(df_clean)}")
    print(f"- Groups compared: {df_clean[\'group\'].unique()}")
    print(f"- Treatments tested: {df_clean[\'treatment\'].unique()}")

if __name__ == "__main__":
    main()
'''
    
    with open(project_path / 'scripts' / 'data_analysis.py', 'w') as f:
        f.write(analysis_script)


def _create_research_paper_example_files(project_path):
    """Create research paper template files."""
    # Create manuscript template
    manuscript_template = '''% Research Paper Template
% Following academic standards and SciTeX framework

\\documentclass[12pt, a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath, amsfonts, amssymb}
\\usepackage{graphicx}
\\usepackage{cite}
\\usepackage{hyperref}
\\usepackage{geometry}
\\geometry{margin=1in}

\\title{Research Paper Title: [Insert Your Title Here]}
\\author{[Your Name]\\\\[Your Institution]\\\\[Your Email]}
\\date{\\today}

\\begin{document}

\\maketitle

\\begin{abstract}
[Write a concise abstract here. Summarize the research problem, methodology, key findings, and implications. Keep it under 250 words.]
\\end{abstract}

\\section{Introduction}

[Introduce the research problem and its significance. Provide background information and clearly state your research objectives and hypotheses.]

\\subsection{Research Questions}
\\begin{itemize}
    \\item [Research Question 1]
    \\item [Research Question 2]
    \\item [Research Question 3]
\\end{itemize}

\\subsection{Hypotheses}
\\begin{itemize}
    \\item [Hypothesis 1]
    \\item [Hypothesis 2]
\\end{itemize}

\\section{Literature Review}

[Review relevant literature and identify the knowledge gap your research addresses.]

\\section{Methodology}

\\subsection{Data Collection}
[Describe your data collection methods and procedures.]

\\subsection{Data Analysis}
[Explain your analytical approach and statistical methods.]

\\subsection{Tools and Software}
[List the tools, software, and frameworks used (including SciTeX).]

\\section{Results}

\\subsection{Descriptive Statistics}
[Present basic descriptive statistics and data overview.]

\\subsection{Main Findings}
[Present your key findings with appropriate tables and figures.]

% Example figure inclusion
% \\begin{figure}[htbp]
%     \\centering
%     \\includegraphics[width=0.8\\textwidth]{../data/figures/results_plot.png}
%     \\caption{Description of your figure}
%     \\label{fig:results}
% \\end{figure}

\\section{Discussion}

\\subsection{Interpretation of Results}
[Interpret your findings in the context of your research questions and hypotheses.]

\\subsection{Implications}
[Discuss the theoretical and practical implications of your research.]

\\subsection{Limitations}
[Acknowledge the limitations of your study.]

\\section{Conclusion}

[Summarize your main findings and their significance. Suggest future research directions.]

\\section{Acknowledgments}

[Acknowledge funding sources, collaborators, and others who contributed to your research.]

\\bibliographystyle{plain}
\\bibliography{references}

\\end{document}
'''
    
    docs_manuscripts_path = project_path / 'docs' / 'manuscripts'
    with open(docs_manuscripts_path / 'manuscript_template.tex', 'w') as f:
        f.write(manuscript_template)
    
    # Create bibliography template
    bibliography_template = '''@article{example2023,
    title={Example Research Paper Title},
    author={Author, First and Coauthor, Second},
    journal={Journal of Example Research},
    volume={10},
    number={1},
    pages={1--15},
    year={2023},
    publisher={Academic Publisher}
}

@book{textbook2022,
    title={Comprehensive Guide to Research Methods},
    author={Expert, Leading},
    year={2022},
    publisher={University Press}
}

@inproceedings{conference2023,
    title={Novel Approach to Data Analysis},
    author={Researcher, Jane and Smith, John},
    booktitle={Proceedings of the International Conference on Data Science},
    pages={123--130},
    year={2023},
    organization={IEEE}
}
'''
    
    with open(docs_manuscripts_path / 'references.bib', 'w') as f:
        f.write(bibliography_template)
    
    # Create research notes template
    notes_template = '''# Research Notes

## Project Overview
- **Title**: [Your Project Title]
- **Start Date**: [Date]
- **Principal Investigator**: [Your Name]
- **Institution**: [Your Institution]

## Research Questions
1. [Question 1]
2. [Question 2]
3. [Question 3]

## Hypotheses
1. [Hypothesis 1]
2. [Hypothesis 2]

## Literature Review Notes

### Key Papers
- **Author et al. (Year)**: [Summary of key findings and relevance]
- **Another Author (Year)**: [Summary and notes]

### Knowledge Gaps Identified
- [Gap 1]: [Description]
- [Gap 2]: [Description]

## Methodology Notes

### Data Collection
- **Source**: [Data source description]
- **Sample Size**: [N = ?]
- **Variables**: [List key variables]
- **Collection Period**: [Dates]

### Analysis Plan
- **Statistical Methods**: [List planned analyses]
- **Software**: Python, R, SPSS, etc.
- **Expected Outputs**: [What results do you expect?]

## Progress Log

### [Date]
- [What was accomplished today]
- [Any issues or challenges]
- [Next steps]

### [Date]
- [Progress update]

## Ideas and Insights

### [Date] - [Topic]
- [Record insights, ideas, or observations]

## Meeting Notes

### [Date] - [Meeting with whom]
- **Agenda**: [What was discussed]
- **Action Items**: [What needs to be done]
- **Follow-up**: [When is next meeting]

## Resources and References

### Useful Links
- [Resource 1]: [URL and description]
- [Resource 2]: [URL and description]

### Contact Information
- **Advisor**: [Name, email, phone]
- **Collaborators**: [Names and contact info]
- **Technical Support**: [IT, statistics help, etc.]

## Data Management

### File Organization
- Raw data location: `data/raw/`
- Processed data: `data/processed/`
- Analysis scripts: `scripts/`
- Results: `results/`

### Backup Strategy
- [How and where data is backed up]
- [Frequency of backups]

### Data Sharing Plan
- [Who has access to data]
- [Data sharing agreements]
- [Publication data availability]

## Timeline and Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Literature Review Complete | [Date] | [ ] |
| Data Collection Complete | [Date] | [ ] |
| Analysis Complete | [Date] | [ ] |
| First Draft Complete | [Date] | [ ] |
| Manuscript Submission | [Date] | [ ] |

## Budget and Resources

### Funding
- **Source**: [Grant, institution, etc.]
- **Amount**: [Budget available]
- **Period**: [Funding period]

### Equipment and Software
- **Computing Resources**: [What\'s available]
- **Software Licenses**: [What\'s needed]
- **Lab Equipment**: [If applicable]

---

*Notes last updated: [Date]*
'''
    
    docs_notes_path = project_path / 'docs' / 'notes'
    with open(docs_notes_path / 'research_notes.md', 'w') as f:
        f.write(notes_template)


def _create_scitex_default_project(project_path):
    """Create default SCITEX project structure from example template."""
    import shutil
    from pathlib import Path
    
    # Path to the example project template
    template_path = Path('/home/ywatanabe/proj/scitex-cloud/docs/to_claude/examples/example-python-project-scitex')
    
    try:
        if template_path.exists():
            # Copy files from template, excluding certain patterns
            exclude_patterns = {
                '.git',
                '__pycache__',
                '.pyc',
                'RUNNING',
                'FINISHED_SUCCESS', 
                'FINISHED_ERROR'
            }
            
            for item in template_path.rglob('*'):
                if item.is_file():
                    # Check if file should be excluded
                    should_exclude = False
                    for pattern in exclude_patterns:
                        if pattern in str(item):
                            should_exclude = True
                            break
                    
                    if not should_exclude:
                        # Calculate relative path from template
                        rel_path = item.relative_to(template_path)
                        dest_file = project_path / rel_path
                        
                        # Create parent directory if needed
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(item, dest_file)
        else:
            print(f"Template path not found: {template_path}")
            # Fall back to creating basic SCITEX structure
            _create_basic_scitex_structure(project_path)
            
    except Exception as e:
        print(f"Error creating SciTeX default project: {e}")
        # Fall back to basic structure
        _create_basic_scitex_structure(project_path)


def _create_basic_scitex_structure(project_path):
    """Create basic SCITEX structure if template is not available."""
    try:
        # Create basic SCITEX directories
        basic_dirs = [
            'config',
            'data/raw',
            'data/processed', 
            'data/figures',
            'data/models',
            'scripts',
            'docs/manuscripts',
            'docs/notes',
            'docs/references',
            'results/outputs',
            'results/reports', 
            'results/analysis',
            'temp/cache',
            'temp/logs',
            'temp/tmp'
        ]
        
        for dir_path in basic_dirs:
            (project_path / dir_path).mkdir(parents=True, exist_ok=True)
            
        # Create basic files
        basic_readme = '''# SciTeX Default Project

This project follows the SCITEX framework for reproducible scientific research.

## Directory Structure

- `config/` - Configuration files
- `data/` - Research data and outputs
  - `raw/` - Original datasets
  - `processed/` - Cleaned data
  - `figures/` - Generated visualizations
  - `models/` - Trained models
- `scripts/` - Analysis scripts
- `docs/` - Documentation
- `results/` - Analysis results
- `temp/` - Temporary files

## Getting Started

1. Add your data to `data/raw/`
2. Create analysis scripts in `scripts/`
3. Document your work in `docs/`
4. View results in `results/`

For more information about SCITEX framework, visit the documentation.
'''
        
        with open(project_path / 'README.md', 'w') as f:
            f.write(basic_readme)
            
        # Create gitkeep files for empty directories
        for dir_path in basic_dirs:
            gitkeep_file = project_path / dir_path / '.gitkeep'
            if not any(gitkeep_file.parent.iterdir()):
                gitkeep_file.touch()
                
    except Exception as e:
        print(f"Error creating basic SCITEX structure: {e}")


def _copy_project_files(source_path, dest_path):
    """Copy files from source project to destination, excluding certain files."""
    import shutil
    
    # Files/directories to exclude from copying
    exclude_patterns = {
        '.scitex_project.json',  # Project metadata
        'temp',  # Temporary files
        '__pycache__',  # Python cache
        '.git',  # Git repository
        'RUNNING',  # Execution markers
        'FINISHED_SUCCESS',
        'FINISHED_ERROR'
    }
    
    try:
        for item in source_path.rglob('*'):
            if item.is_file():
                # Check if file should be excluded
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern in str(item):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    # Calculate relative path from source
                    rel_path = item.relative_to(source_path)
                    dest_file = dest_path / rel_path
                    
                    # Create parent directory if needed
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(item, dest_file)
    except Exception as e:
        print(f"Error copying files: {e}")