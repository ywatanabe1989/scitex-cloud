# Collaborator Management UI - Next Session

## Backend Complete ✅
- add_collaborator(request, project_id) - Add user by username
- remove_collaborator(request, project_id, collaborator_id) - Remove user

## URLs Needed
Add to apps/writer_app/urls.py:
```python
path('project/<int:project_id>/collaborators/add/', views.add_collaborator, name='add_collaborator'),
path('project/<int:project_id>/collaborators/<int:collaborator_id>/remove/', views.remove_collaborator, name='remove_collaborator'),
```

## UI to Add
In apps/writer_app/templates/writer_app/project_writer.html around line 775:

1. Add "+" button next to "Active Collaborators" header
2. Show all manuscript.collaborators.all (not just online ones)
3. Add modal/form for entering username
4. Add remove buttons for each collaborator

## JavaScript Needed
```javascript
// Add collaborator
document.getElementById('add-collaborator-btn').addEventListener('click', async () => {
    const username = prompt('Enter username to add:');
    if (username) {
        const response = await fetch(`/writer/project/${projectId}/collaborators/add/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken()},
            body: JSON.stringify({username})
        });
        const data = await response.json();
        if (data.success) {
            showToast(`Added ${username} as collaborator`, 'success');
            location.reload();
        } else {
            showToast(data.error, 'danger');
        }
    }
});
```

## Quick Fix for Now
Users can add project collaborators from project settings, and they automatically become manuscript collaborators.
