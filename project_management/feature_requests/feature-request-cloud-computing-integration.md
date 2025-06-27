# Feature Request: Cloud Computing Integration with Job Scheduler

**Date**: 2025-05-23
**Priority**: High
**Category**: Infrastructure & Scalability

## Summary

Implement a job scheduling system (like SLURM) integrated with major cloud computing platforms (AWS, Google Cloud, Azure) to provide scalable computational resources for SciTeX users.

## Current Situation

- Users are limited to local server resources
- No job queuing or resource management system
- Cannot scale for computationally intensive tasks
- No integration with cloud storage services

## Proposed Solution

### 1. Job Scheduling System

Implement a SLURM-like scheduler with Django integration:

```python
# apps/compute_app/models.py
class ComputeJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=50)  # 'engine', 'code', 'viz'
    status = models.CharField(max_length=20)  # 'queued', 'running', 'completed', 'failed'
    priority = models.IntegerField(default=0)
    
    # Resource requirements
    cpu_cores = models.IntegerField(default=1)
    memory_gb = models.IntegerField(default=4)
    gpu_type = models.CharField(max_length=50, blank=True)
    estimated_hours = models.FloatField(default=1.0)
    
    # Cloud provider
    provider = models.CharField(max_length=20)  # 'local', 'aws', 'gcp', 'azure'
    instance_type = models.CharField(max_length=50, blank=True)
    
    # Job details
    script_path = models.TextField()
    input_data = models.JSONField()
    output_path = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    
    # Results
    exit_code = models.IntegerField(null=True)
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
```

### 2. Cloud Provider Integration

#### AWS Integration
```python
# apps/compute_app/providers/aws.py
import boto3
from celery import shared_task

class AWSComputeProvider:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.batch = boto3.client('batch')
        self.s3 = boto3.client('s3')
    
    def submit_job(self, job):
        # Create spot instance or use AWS Batch
        response = self.batch.submit_job(
            jobName=f'scitex-job-{job.id}',
            jobQueue='scitex-queue',
            jobDefinition='scitex-compute',
            parameters={
                'cores': str(job.cpu_cores),
                'memory': str(job.memory_gb * 1024),
                'script': job.script_path
            }
        )
        return response['jobId']
    
    def get_instance_pricing(self, instance_type, hours):
        # Calculate spot/on-demand pricing
        pass
```

#### Google Cloud Integration
```python
# apps/compute_app/providers/gcp.py
from google.cloud import compute_v1, storage

class GCPComputeProvider:
    def __init__(self):
        self.compute = compute_v1.InstancesClient()
        self.storage = storage.Client()
    
    def submit_job(self, job):
        # Create preemptible instance or use Cloud Run
        instance = compute_v1.Instance(
            name=f'scitex-job-{job.id}',
            machine_type=self._get_machine_type(job),
            scheduling=compute_v1.Scheduling(
                preemptible=True,
                automatic_restart=False
            )
        )
        # Launch and monitor instance
        pass
```

### 3. Job Scheduler Implementation

```python
# apps/compute_app/scheduler.py
from celery import shared_task
from django.db import transaction
import redis

class SciTeXScheduler:
    def __init__(self):
        self.redis = redis.Redis()
        self.providers = {
            'aws': AWSComputeProvider(),
            'gcp': GCPComputeProvider(),
            'azure': AzureComputeProvider(),
            'local': LocalComputeProvider()
        }
    
    def submit_job(self, user, job_config):
        # Check user quotas
        if not self.check_user_quota(user, job_config):
            raise QuotaExceededException()
        
        # Estimate costs
        cost_estimate = self.estimate_cost(job_config)
        
        # Create job record
        job = ComputeJob.objects.create(
            user=user,
            **job_config,
            cost_estimate=cost_estimate
        )
        
        # Queue job
        queue_job.delay(job.id)
        return job
    
    @shared_task
    def queue_job(self, job_id):
        job = ComputeJob.objects.get(id=job_id)
        
        # Select best provider based on requirements
        provider = self.select_provider(job)
        
        # Submit to provider
        provider_job_id = self.providers[provider].submit_job(job)
        
        # Update job record
        job.provider_job_id = provider_job_id
        job.status = 'running'
        job.started_at = timezone.now()
        job.save()
        
        # Monitor job
        monitor_job.delay(job.id)
```

### 4. Storage Integration

```python
# apps/compute_app/storage.py
class CloudStorageManager:
    def __init__(self):
        self.providers = {
            's3': S3Storage(),
            'gcs': GoogleCloudStorage(),
            'azure': AzureStorage()
        }
    
    def sync_input_data(self, job):
        # Upload input data to cloud storage
        provider = self.providers[job.provider]
        input_url = provider.upload(job.input_data)
        return input_url
    
    def retrieve_output(self, job):
        # Download results from cloud storage
        provider = self.providers[job.provider]
        output_data = provider.download(job.output_path)
        return output_data
```

### 5. User Interface

```html
<!-- templates/compute/job_submission.html -->
<div class="job-submission-form">
  <h2>Submit Compute Job</h2>
  
  <form method="post">
    {% csrf_token %}
    
    <!-- Job Type -->
    <div class="form-group">
      <label>Job Type</label>
      <select name="job_type" class="form-control">
        <option value="code">SciTeX Code Analysis</option>
        <option value="engine">SciTeX Engine Processing</option>
        <option value="viz">SciTeX Viz Rendering</option>
      </select>
    </div>
    
    <!-- Resource Requirements -->
    <div class="resource-config">
      <h3>Resource Requirements</h3>
      <div class="row">
        <div class="col-md-3">
          <label>CPU Cores</label>
          <input type="number" name="cpu_cores" min="1" max="96" value="4">
        </div>
        <div class="col-md-3">
          <label>Memory (GB)</label>
          <input type="number" name="memory_gb" min="1" max="768" value="16">
        </div>
        <div class="col-md-3">
          <label>GPU Type</label>
          <select name="gpu_type">
            <option value="">None</option>
            <option value="t4">NVIDIA T4</option>
            <option value="v100">NVIDIA V100</option>
            <option value="a100">NVIDIA A100</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- Provider Selection -->
    <div class="provider-selection">
      <h3>Compute Provider</h3>
      <div class="provider-options">
        <label class="provider-option">
          <input type="radio" name="provider" value="auto" checked>
          <span>Auto-select (Best Price)</span>
        </label>
        <label class="provider-option">
          <input type="radio" name="provider" value="aws">
          <span>AWS EC2/Batch</span>
        </label>
        <label class="provider-option">
          <input type="radio" name="provider" value="gcp">
          <span>Google Cloud</span>
        </label>
        <label class="provider-option">
          <input type="radio" name="provider" value="azure">
          <span>Azure</span>
        </label>
      </div>
    </div>
    
    <!-- Cost Estimate -->
    <div class="cost-estimate">
      <h3>Estimated Cost</h3>
      <div id="cost-breakdown">
        <p>Compute: $<span id="compute-cost">0.00</span></p>
        <p>Storage: $<span id="storage-cost">0.00</span></p>
        <p>Transfer: $<span id="transfer-cost">0.00</span></p>
        <p><strong>Total: $<span id="total-cost">0.00</span></strong></p>
      </div>
    </div>
    
    <button type="submit" class="btn btn-primary">Submit Job</button>
  </form>
</div>
```

### 6. Job Monitoring Dashboard

```python
# apps/compute_app/views.py
class JobDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'compute/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_jobs = ComputeJob.objects.filter(user=self.request.user)
        
        context['active_jobs'] = user_jobs.filter(
            status__in=['queued', 'running']
        )
        context['completed_jobs'] = user_jobs.filter(
            status='completed'
        ).order_by('-completed_at')[:10]
        
        # Calculate usage statistics
        context['total_compute_hours'] = user_jobs.aggregate(
            total=Sum('actual_hours')
        )['total'] or 0
        
        context['total_cost'] = user_jobs.aggregate(
            total=Sum('actual_cost')
        )['total'] or 0
        
        return context
```

## Implementation Plan

### Phase 1: Local SLURM Integration (Month 1)
1. Set up SLURM on local cluster
2. Create Django models and basic scheduler
3. Implement job submission interface
4. Basic monitoring dashboard

### Phase 2: AWS Integration (Month 2)
1. AWS Batch setup
2. S3 storage integration
3. Cost estimation for AWS
4. Spot instance support

### Phase 3: Google Cloud Integration (Month 3)
1. GCP Compute Engine setup
2. Cloud Storage integration
3. Preemptible instance support
4. Cloud Run for serverless jobs

### Phase 4: Multi-Cloud Optimization (Month 4)
1. Intelligent provider selection
2. Cost optimization algorithms
3. Data transfer optimization
4. Advanced monitoring

## Benefits

1. **Scalability**: Handle any workload size
2. **Cost Efficiency**: Use spot/preemptible instances
3. **Flexibility**: Choose best provider for each job
4. **Accessibility**: Democratize access to HPC resources
5. **Integration**: Seamless with existing SciTeX tools

## Cost Structure

### For Users
- Pay-per-use: Only pay for resources consumed
- Transparent pricing: See costs before submission
- Budget controls: Set monthly/project limits

### For Platform
- Markup: 10-20% on cloud provider costs
- Volume discounts: Negotiate better rates
- Reserved instances: For predictable workloads

## Security Considerations

1. **Data Isolation**: Separate VPCs per user/project
2. **Encryption**: At-rest and in-transit
3. **Access Control**: IAM roles and policies
4. **Compliance**: HIPAA/GDPR options available

## Success Metrics

- Job completion rate > 99%
- Cost savings vs on-demand: 50-70%
- User satisfaction: 4.5+ stars
- Platform revenue: $50K/month within 6 months

## Alternatives Considered

1. **Kubernetes Only**: Less suitable for HPC workloads
2. **Single Cloud Provider**: Vendor lock-in risk
3. **Pure Serverless**: Limited for long-running jobs

## Conclusion

This cloud computing integration will transform SciTeX from a single-server platform to a globally scalable research infrastructure, enabling researchers to run complex analyses without infrastructure constraints.