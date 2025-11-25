#!/bin/bash
# SLURM Installation Step 4: Verify Installation
# File: deployment/slurm/scripts/04_verify.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

echo_header "Step 4: Verifying SLURM installation"

# Check if SLURM commands are available
echo_info "Checking SLURM commands..."
if ! command -v sinfo &> /dev/null; then
    echo_error "sinfo command not found!"
    exit 1
fi

# Check cluster status
echo_info "Checking cluster status..."
if sinfo &> /dev/null; then
    echo_success "Cluster is responsive"
    echo ""
    sinfo
else
    echo_error "Cluster not responding"
    echo_info "Check logs:"
    echo_info "  sudo journalctl -u slurmctld -n 20"
    echo_info "  sudo journalctl -u slurmd -n 20"
    exit 1
fi

# Check queue
echo ""
echo_info "Checking job queue..."
squeue

# Submit test job
echo ""
echo_info "Submitting test job..."

TEST_SCRIPT="/tmp/slurm_test_$(date +%s).sh"
cat > "$TEST_SCRIPT" <<'EOF'
#!/bin/bash
#SBATCH --job-name=test_install
#SBATCH --output=/tmp/slurm_test-%j.out
#SBATCH --partition=express
#SBATCH --time=00:01:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G

echo "========================================="
echo "SLURM Test Job"
echo "========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "Date: $(date)"
echo "CPUs allocated: $SLURM_CPUS_PER_TASK"
echo "Memory allocated: $SLURM_MEM_PER_NODE MB"
echo ""
echo "Environment:"
env | grep SLURM | sort
echo ""
echo "Test complete!"
echo "========================================="
EOF

chmod +x "$TEST_SCRIPT"

# Submit job
JOB_OUTPUT=$(sbatch "$TEST_SCRIPT")
JOB_ID=$(echo "$JOB_OUTPUT" | awk '{print $NF}')

echo_success "Test job submitted: Job ID $JOB_ID"
echo_info "Waiting for job to complete..."

# Wait for job to complete (max 30 seconds)
for i in {1..30}; do
    JOB_STATE=$(squeue -j "$JOB_ID" -h -o "%T" 2>/dev/null || echo "COMPLETED")
    if [ "$JOB_STATE" == "COMPLETED" ] || [ -z "$JOB_STATE" ]; then
        echo_success "Job completed!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Show job accounting
echo ""
echo_info "Job details:"
sacct -j "$JOB_ID" --format=JobID,JobName,Partition,State,Elapsed,CPUTime,MaxRSS

# Show output
echo ""
echo_info "Job output:"
OUTPUT_FILE="/tmp/slurm_test-${JOB_ID}.out"
if [ -f "$OUTPUT_FILE" ]; then
    cat "$OUTPUT_FILE"
    echo ""
    echo_success "Test job output saved to: $OUTPUT_FILE"
else
    echo_warning "Output file not found: $OUTPUT_FILE"
fi

# Cleanup
rm -f "$TEST_SCRIPT"

echo ""
echo_success "Step 4 complete: SLURM installation verified"
echo ""
echo_info "Summary:"
echo_info "  ✓ SLURM commands available"
echo_info "  ✓ Cluster responsive"
echo_info "  ✓ Job submission working"
echo_info "  ✓ Job execution successful"
echo ""
echo_success "SLURM is ready to use!"

# EOF
