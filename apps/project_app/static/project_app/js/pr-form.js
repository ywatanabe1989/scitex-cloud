// Pull request form functionality

function updateComparison() {
    const base = document.getElementById('baseSelect').value;
    const head = document.getElementById('headSelect').value;

    if (base && head) {
        window.location.href = `?base=${base}&head=${head}`;
    }
}
