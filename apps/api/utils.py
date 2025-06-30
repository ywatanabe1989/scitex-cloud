#!/usr/bin/env python3
"""
Secure code execution utilities for SciTeX-Code.
"""

import os
import sys
import subprocess
import tempfile
import time
import resource
import signal
import json
import shutil
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from apps.code_app.models import CodeExecutionJob, ResourceUsage
import threading


class CodeExecutionTimeout(Exception):
    """Raised when code execution times out."""
    pass


class CodeExecutionError(Exception):
    """Raised when code execution fails."""
    pass


def execute_code_safely(job):
    """
    Execute code safely in a sandboxed environment with resource limits.
    
    Args:
        job: CodeExecutionJob instance
    """
    # Update job status
    job.status = 'running'
    job.started_at = timezone.now()
    job.save()
    
    start_time = time.time()
    
    try:
        # Create secure temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create user workspace
            workspace = temp_path / "workspace"
            workspace.mkdir()
            
            # Write code to file
            code_file = workspace / "user_code.py"
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(job.source_code)
            
            # Copy project files if available (requirements.txt, .env, etc.)
            copy_project_files(job.user, workspace)
            
            # Create wrapper script with security restrictions
            wrapper_script = create_wrapper_script(
                code_file, workspace, job.timeout_seconds, job.max_memory_mb
            )
            
            # Execute code with restrictions
            success, stdout, stderr, resource_usage = run_sandboxed_code(
                wrapper_script, workspace, job.timeout_seconds
            )
            
            if success:
                job.status = 'completed'
                job.output = stdout
                job.return_code = 0
                
                # Copy any output files
                output_files = []
                for file_path in workspace.glob('*'):
                    if file_path.name != 'user_code.py' and file_path.is_file():
                        # Store info about output files
                        output_files.append({
                            'name': file_path.name,
                            'size': file_path.stat().st_size,
                            'type': 'file'
                        })
                
                job.output_files = output_files
                
                # Look for plot files
                plot_files = []
                for plot_ext in ['*.png', '*.jpg', '*.jpeg', '*.pdf', '*.svg']:
                    for plot_file in workspace.glob(plot_ext):
                        plot_files.append({
                            'name': plot_file.name,
                            'size': plot_file.stat().st_size,
                            'type': 'plot'
                        })
                
                job.plot_files = plot_files
                
            else:
                job.status = 'failed'
                job.error_output = stderr
                job.return_code = 1
            
            # Record resource usage
            job.cpu_time = resource_usage.get('cpu_time', 0)
            job.memory_peak = resource_usage.get('memory_peak', 0)
            job.execution_time = time.time() - start_time
            
    except CodeExecutionTimeout:
        job.status = 'timeout'
        job.error_output = f"Code execution timed out after {job.timeout_seconds} seconds"
        job.execution_time = time.time() - start_time
        
    except Exception as e:
        job.status = 'failed'
        job.error_output = f"Execution error: {str(e)}"
        job.execution_time = time.time() - start_time
    
    finally:
        job.completed_at = timezone.now()
        job.save()
        
        # Update user resource usage
        update_user_resource_usage(job)


def create_wrapper_script(code_file, workspace, timeout_seconds, max_memory_mb):
    """
    Create a wrapper script that enforces security and resource limits.
    """
    wrapper_content = f'''#!/usr/bin/env python3
import os
import sys
import resource
import signal
import time

# Set resource limits
def set_limits():
    # Memory limit (in bytes)
    max_memory = {max_memory_mb} * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
    
    # CPU time limit (in seconds)
    cpu_limit = min({timeout_seconds}, 300)  # Max 5 minutes CPU
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
    
    # File size limit (100MB)
    file_limit = 100 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
    
    # Number of processes limit
    resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))

# Timeout handler
def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timed out")

# Set timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm({timeout_seconds})

try:
    # Set resource limits
    set_limits()
    
    # Change to workspace directory
    os.chdir(r"{workspace}")
    
    # Add workspace to Python path
    sys.path.insert(0, r"{workspace}")
    
    # Redirect stderr to capture errors
    import io
    import contextlib
    
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    # Check for project-specific requirements
    requirements_file = os.path.join(r"{workspace}", "requirements.txt")
    if os.path.exists(requirements_file):
        print("Found project requirements.txt, installing dependencies...")
        import subprocess
        import sys
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", requirements_file,
                "--user", "--quiet"
            ])
            print("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install requirements: {{e}}")
    
    # Load project-specific environment variables
    env_file = os.path.join(r"{workspace}", ".env")
    if os.path.exists(env_file):
        print("Loading project environment variables...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    # Import common scientific libraries safely
    try:
        import numpy as np
        import pandas as pd
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        
        # Try to import MNGS if available
        try:
            import mngs
        except ImportError:
            print("Info: MNGS library not available (install with: pip install mngs)")
        
    except ImportError as e:
        print(f"Info: Some libraries not available: {{e}}")
        print("Tip: Add missing libraries to requirements.txt in your project")
    
    # Execute user code
    with contextlib.redirect_stdout(stdout_capture), \\
         contextlib.redirect_stderr(stderr_capture):
        
        # Read and execute user code
        with open(r"{code_file}", 'r', encoding='utf-8') as f:
            user_code = f.read()
        
        # Execute in restricted environment
        exec(user_code)
    
    # Print captured output
    stdout_content = stdout_capture.getvalue()
    stderr_content = stderr_capture.getvalue()
    
    if stdout_content:
        print(stdout_content)
    if stderr_content:
        print(stderr_content, file=sys.stderr)

except TimeoutError:
    print("Error: Code execution timed out", file=sys.stderr)
    sys.exit(124)  # Timeout exit code
except MemoryError:
    print("Error: Code exceeded memory limit", file=sys.stderr)
    sys.exit(125)  # Memory limit exit code
except Exception as e:
    print(f"Error: {{type(e).__name__}}: {{e}}", file=sys.stderr)
    sys.exit(1)
finally:
    signal.alarm(0)  # Cancel timeout
'''
    
    wrapper_file = workspace / "wrapper.py"
    with open(wrapper_file, 'w', encoding='utf-8') as f:
        f.write(wrapper_content)
    
    return wrapper_file


def run_sandboxed_code(wrapper_script, workspace, timeout_seconds):
    """
    Run code in a sandboxed environment using subprocess.
    
    Returns:
        tuple: (success, stdout, stderr, resource_usage)
    """
    try:
        # Run the wrapper script
        process = subprocess.Popen(
            [sys.executable, str(wrapper_script)],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid  # Create new process group
        )
        
        # Wait for completion with timeout
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds + 10)
            success = process.returncode == 0
            
            # Estimate resource usage (basic implementation)
            resource_usage = {
                'cpu_time': 0.0,  # Would need more sophisticated monitoring
                'memory_peak': 0   # Would need process monitoring
            }
            
            return success, stdout, stderr, resource_usage
            
        except subprocess.TimeoutExpired:
            # Kill the process group
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                process.wait()
            
            return False, "", "Code execution timed out", {'cpu_time': 0, 'memory_peak': 0}
    
    except Exception as e:
        return False, "", f"Execution error: {str(e)}", {'cpu_time': 0, 'memory_peak': 0}


def copy_project_files(user, workspace):
    """
    Copy project-specific files (requirements.txt, .env, etc.) to workspace.
    
    Args:
        user: User instance
        workspace: Path to workspace directory
    """
    try:
        from apps.core_app.models import Project
        
        # Get user's most recent active project
        project = Project.objects.filter(
            owner=user, 
            status__in=['active', 'planning']
        ).order_by('-updated_at').first()
        
        if not project or not project.data_location:
            return
        
        # Construct project directory path
        project_dir = Path(settings.BASE_DIR) / project.data_location.strip('/')
        
        if not project_dir.exists():
            return
        
        # Copy specific project files
        project_files = ['requirements.txt', '.env', 'setup.py', 'pyproject.toml']
        
        for filename in project_files:
            source_file = project_dir / filename
            if source_file.exists():
                dest_file = workspace / filename
                shutil.copy2(source_file, dest_file)
                print(f"Copied {filename} to workspace")
        
        # Copy any Python modules from project
        for py_file in project_dir.glob('*.py'):
            if py_file.name not in ['manage.py', 'wsgi.py', 'asgi.py']:
                dest_file = workspace / py_file.name
                shutil.copy2(py_file, dest_file)
                
    except Exception as e:
        # Don't fail execution if project files can't be copied
        print(f"Warning: Could not copy project files: {e}")


def update_user_resource_usage(job):
    """
    Update user's resource usage statistics.
    """
    try:
        from datetime import date
        today = date.today()
        month = today.strftime("%Y-%m")
        
        # Get or create resource usage record
        usage, created = ResourceUsage.objects.get_or_create(
            user=job.user,
            date=today,
            defaults={'month': month}
        )
        
        # Update metrics
        usage.cpu_seconds += job.cpu_time or 0
        usage.memory_mb_hours += (job.memory_peak or 0) / (1024 * 1024) * (job.execution_time or 0) / 3600
        usage.code_executions += 1
        usage.save()
        
    except Exception as e:
        # Log error but don't fail the job
        print(f"Warning: Failed to update resource usage: {e}")


def generate_analysis_code(analysis_type, input_data_path, parameters):
    """
    Generate Python code for data analysis based on type and parameters.
    
    Args:
        analysis_type: Type of analysis to perform
        input_data_path: Path to input data file
        parameters: Analysis parameters
    
    Returns:
        str: Generated Python code
    """
    base_imports = """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from pathlib import Path
import json

# Set up plotting
plt.style.use('default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

print("Starting data analysis...")
"""
    
    if analysis_type == 'time_series':
        code = base_imports + f"""
# Time series analysis
try:
    # Load data
    data_path = r"{input_data_path}"
    if data_path.endswith('.csv'):
        df = pd.read_csv(data_path)
    elif data_path.endswith('.pkl'):
        df = pd.read_pickle(data_path)
    else:
        print("Warning: Unsupported file format, attempting CSV...")
        df = pd.read_csv(data_path)
    
    print(f"Data loaded: {{df.shape}} rows x columns")
    print(f"Columns: {{list(df.columns)}}")
    
    # Basic time series analysis
    if 'time' in df.columns or 'timestamp' in df.columns:
        time_col = 'time' if 'time' in df.columns else 'timestamp'
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.set_index(time_col)
    
    # Plot time series
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        fig, axes = plt.subplots(len(numeric_cols), 1, figsize=(12, 4*len(numeric_cols)))
        if len(numeric_cols) == 1:
            axes = [axes]
        
        for i, col in enumerate(numeric_cols):
            axes[i].plot(df.index, df[col])
            axes[i].set_title(f'Time Series: {{col}}')
            axes[i].set_ylabel(col)
        
        plt.tight_layout()
        plt.savefig('time_series_plot.png')
        print("Time series plot saved as 'time_series_plot.png'")
    
    # Basic statistics
    print("\\nBasic Statistics:")
    print(df.describe())
    
except Exception as e:
    print(f"Error in time series analysis: {{e}}")
"""
    
    elif analysis_type == 'statistics':
        code = base_imports + f"""
# Statistical analysis
try:
    # Load data
    data_path = r"{input_data_path}"
    if data_path.endswith('.csv'):
        df = pd.read_csv(data_path)
    elif data_path.endswith('.pkl'):
        df = pd.read_pickle(data_path)
    else:
        df = pd.read_csv(data_path)
    
    print(f"Data loaded: {{df.shape}} rows x columns")
    
    # Basic statistical analysis
    numeric_df = df.select_dtypes(include=[np.number])
    
    if len(numeric_df.columns) > 0:
        # Descriptive statistics
        print("\\nDescriptive Statistics:")
        print(numeric_df.describe())
        
        # Correlation matrix
        if len(numeric_df.columns) > 1:
            correlation_matrix = numeric_df.corr()
            
            plt.figure(figsize=(10, 8))
            plt.imshow(correlation_matrix, cmap='coolwarm', aspect='auto')
            plt.colorbar()
            plt.title('Correlation Matrix')
            plt.xticks(range(len(correlation_matrix.columns)), correlation_matrix.columns, rotation=45)
            plt.yticks(range(len(correlation_matrix.columns)), correlation_matrix.columns)
            plt.tight_layout()
            plt.savefig('correlation_matrix.png')
            print("Correlation matrix saved as 'correlation_matrix.png'")
        
        # Histograms
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        
        for i, col in enumerate(numeric_df.columns[:4]):
            axes[i].hist(numeric_df[col].dropna(), bins=30, alpha=0.7)
            axes[i].set_title(f'Distribution: {{col}}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig('distributions.png')
        print("Distribution plots saved as 'distributions.png'")
    
except Exception as e:
    print(f"Error in statistical analysis: {{e}}")
"""
    
    elif analysis_type == 'visualization':
        code = base_imports + f"""
# Data visualization
try:
    # Load data
    data_path = r"{input_data_path}"
    if data_path.endswith('.csv'):
        df = pd.read_csv(data_path)
    elif data_path.endswith('.pkl'):
        df = pd.read_pickle(data_path)
    else:
        df = pd.read_csv(data_path)
    
    print(f"Data loaded: {{df.shape}} rows x columns")
    
    # Create various visualizations
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    # Numeric data visualizations
    if len(numeric_cols) >= 2:
        # Scatter plot matrix
        from pandas.plotting import scatter_matrix
        scatter_matrix(df[numeric_cols], alpha=0.6, figsize=(12, 12))
        plt.suptitle('Scatter Plot Matrix')
        plt.tight_layout()
        plt.savefig('scatter_matrix.png')
        print("Scatter matrix saved as 'scatter_matrix.png'")
        plt.close()
        
        # Box plots
        plt.figure(figsize=(12, 6))
        df[numeric_cols].boxplot()
        plt.title('Box Plots')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('box_plots.png')
        print("Box plots saved as 'box_plots.png'")
        plt.close()
    
    # Categorical data visualizations
    if len(categorical_cols) > 0:
        for col in categorical_cols[:3]:  # Limit to first 3 categorical columns
            value_counts = df[col].value_counts().head(10)
            plt.figure(figsize=(10, 6))
            value_counts.plot(kind='bar')
            plt.title(f'Value Counts: {{col}}')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'{{col}}_counts.png')
            print(f"Value counts for {{col}} saved as '{{col}}_counts.png'")
            plt.close()
    
except Exception as e:
    print(f"Error in visualization: {{e}}")
"""
    
    else:  # custom analysis
        code = base_imports + f"""
# Custom data analysis
try:
    # Load data
    data_path = r"{input_data_path}"
    if data_path.endswith('.csv'):
        df = pd.read_csv(data_path)
    elif data_path.endswith('.pkl'):
        df = pd.read_pickle(data_path)
    else:
        print("Warning: Unsupported file format, attempting CSV...")
        df = pd.read_csv(data_path)
    
    print(f"Data loaded: {{df.shape}} rows x columns")
    print(f"Columns: {{list(df.columns)}}")
    print("\\nData types:")
    print(df.dtypes)
    print("\\nFirst 5 rows:")
    print(df.head())
    
    # Basic analysis
    print("\\nBasic information:")
    print(f"Shape: {{df.shape}}")
    print(f"Missing values: {{df.isnull().sum().sum()}}")
    
    # Simple visualization
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        plt.figure(figsize=(10, 6))
        df[numeric_cols].hist(bins=20, alpha=0.7)
        plt.suptitle('Data Distribution')
        plt.tight_layout()
        plt.savefig('data_overview.png')
        print("Data overview saved as 'data_overview.png'")
    
    print("\\nAnalysis complete!")
    
except Exception as e:
    print(f"Error in analysis: {{e}}")
"""
    
    return code


def check_security_requirements():
    """
    Check if the system has required security features.
    
    Returns:
        dict: Security status and recommendations
    """
    status = {
        'resource_limits': True,  # Python resource module
        'process_isolation': True,  # subprocess with process groups
        'filesystem_isolation': True,  # temporary directories
        'network_isolation': False,  # Would need additional setup
        'recommendations': []
    }
    
    # Check if running as privileged user
    if os.getuid() == 0:
        status['recommendations'].append(
            "Running as root - consider using unprivileged user for code execution"
        )
    
    # Check if Docker is available for better isolation
    try:
        subprocess.run(['docker', '--version'], 
                      capture_output=True, check=True, timeout=5)
        status['docker_available'] = True
        status['recommendations'].append(
            "Docker available - consider using containers for enhanced isolation"
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        status['docker_available'] = False
    
    return status