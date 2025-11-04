// Workflow run detail page functionality

function toggleJob(jobId) {
    const stepsDiv = document.getElementById(`job-${jobId}-steps`);
    const chevron = document.getElementById(`job-${jobId}-chevron`);

    stepsDiv.classList.toggle('show');

    if (stepsDiv.classList.contains('show')) {
        chevron.classList.remove('bi-chevron-down');
        chevron.classList.add('bi-chevron-up');
    } else {
        chevron.classList.remove('bi-chevron-up');
        chevron.classList.add('bi-chevron-down');
    }
}

function toggleStep(stepId) {
    const outputDiv = document.getElementById(`step-${stepId}-output`);
    const chevron = document.getElementById(`step-${stepId}-chevron`);

    outputDiv.classList.toggle('show');

    if (outputDiv.classList.contains('show')) {
        chevron.classList.remove('bi-chevron-down');
        chevron.classList.add('bi-chevron-up');
    } else {
        chevron.classList.remove('bi-chevron-up');
        chevron.classList.add('bi-chevron-down');
    }
}

// Auto-refresh for in-progress runs
document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.container-fluid');
    if (container && container.dataset.runStatus === 'in_progress') {
        setTimeout(function() {
            location.reload();
        }, 5000); // Refresh every 5 seconds
    }
});
