"""
SciTeX Cloud - Permission Middleware and Decorators

This module provides permission checking middleware and decorators for 
project-based file access control as described in the groups and permissions 
documentation.
"""

from functools import wraps
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project


def require_project_permission(permission):
    """
    Decorator to require specific project permission before accessing files.
    
    Usage:
        @require_project_permission('can_read_files')
        def read_file(request, project_id, file_path):
            # Access granted - proceed with file operation
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, project_id, *args, **kwargs):
            # Get project and check if user has permission
            project = get_object_or_404(Project, id=project_id)
            
            # Check if user has access to the project
            if not project.is_accessible_by(request.user):
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'You do not have access to this project'
                    }, status=403)
                else:
                    return HttpResponseForbidden('You do not have access to this project')
            
            # Check specific permission
            if not project.has_permission(request.user, permission):
                permission_name = permission.replace('can_', '').replace('_', ' ')
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'status': 'error',
                        'message': f'You do not have permission to {permission_name} in this project'
                    }, status=403)
                else:
                    return HttpResponseForbidden(f'You do not have permission to {permission_name} in this project')
            
            # Permission granted - add project to request for view use
            request.project = project
            return view_func(request, project_id, *args, **kwargs)
        
        return wrapper
    return decorator


def require_project_access(minimum_role=None):
    """
    Decorator to require minimum project access role.
    
    Args:
        minimum_role: Minimum role required ('viewer', 'collaborator', 'editor', 'admin', 'owner')
    
    Usage:
        @require_project_access('editor')
        def edit_project(request, project_id):
            # User has at least editor role
    """
    # Role hierarchy for permission checking
    role_hierarchy = {
        'viewer': 0,
        'collaborator': 1, 
        'editor': 2,
        'admin': 3,
        'owner': 4
    }
    
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, project_id, *args, **kwargs):
            project = get_object_or_404(Project, id=project_id)
            
            # Check if user has access
            if not project.is_accessible_by(request.user):
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'You do not have access to this project'
                    }, status=403)
                else:
                    return HttpResponseForbidden('You do not have access to this project')
            
            # Check minimum role if specified
            if minimum_role:
                user_role = project.get_user_role(request.user)
                if not user_role:
                    return HttpResponseForbidden('You are not a member of this project')
                
                user_level = role_hierarchy.get(user_role, 0)
                required_level = role_hierarchy.get(minimum_role, 0)
                
                if user_level < required_level:
                    if request.headers.get('Accept') == 'application/json':
                        return JsonResponse({
                            'status': 'error',
                            'message': f'You need at least {minimum_role} role to access this resource'
                        }, status=403)
                    else:
                        return HttpResponseForbidden(f'You need at least {minimum_role} role to access this resource')
            
            # Access granted
            request.project = project
            request.user_role = project.get_user_role(request.user)
            return view_func(request, project_id, *args, **kwargs)
        
        return wrapper
    return decorator


def can_edit_project(user, project):
    """Check if user can edit project metadata"""
    return project.can_edit_metadata(user)


def can_manage_collaborators(user, project):
    """Check if user can manage project collaborators"""
    return project.can_manage_collaborators(user)


def can_read_files(user, project):
    """Check if user can read project files"""
    return project.can_read_files(user)


def can_write_files(user, project):
    """Check if user can write project files"""
    return project.can_write_files(user)


def can_delete_files(user, project):
    """Check if user can delete project files"""
    return project.can_delete_files(user)


def can_run_analysis(user, project):
    """Check if user can run analysis/code"""
    return project.can_run_analysis(user)


class ProjectPermissionMixin:
    """
    Mixin for views that need project permission checking.
    
    Usage:
        class ProjectFileView(ProjectPermissionMixin, View):
            required_permission = 'can_read_files'
            
            def get(self, request, project_id):
                # self.project and permissions already checked
                return JsonResponse({'files': self.project.list_files()})
    """
    
    required_permission = None
    minimum_role = None
    
    def dispatch(self, request, project_id, *args, **kwargs):
        """Check permissions before dispatching to view method"""
        # Get project
        try:
            self.project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({
                'status': 'error', 
                'message': 'Project not found'
            }, status=404)
        
        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=401)
        
        # Check basic access
        if not self.project.is_accessible_by(request.user):
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have access to this project'
            }, status=403)
        
        # Check specific permission
        if self.required_permission and not self.project.has_permission(request.user, self.required_permission):
            permission_name = self.required_permission.replace('can_', '').replace('_', ' ')
            return JsonResponse({
                'status': 'error',
                'message': f'You do not have permission to {permission_name} in this project'
            }, status=403)
        
        # Check minimum role
        if self.minimum_role:
            role_hierarchy = {
                'viewer': 0, 'collaborator': 1, 'editor': 2, 'admin': 3, 'owner': 4
            }
            user_role = self.project.get_user_role(request.user)
            if not user_role:
                return JsonResponse({
                    'status': 'error',
                    'message': 'You are not a member of this project'
                }, status=403)
            
            user_level = role_hierarchy.get(user_role, 0)
            required_level = role_hierarchy.get(self.minimum_role, 0)
            
            if user_level < required_level:
                return JsonResponse({
                    'status': 'error',
                    'message': f'You need at least {self.minimum_role} role to access this resource'
                }, status=403)
        
        # Store user role for view use
        self.user_role = self.project.get_user_role(request.user)
        
        return super().dispatch(request, project_id, *args, **kwargs)


def bulk_permission_check(user, project, permissions):
    """
    Check multiple permissions at once for efficiency.
    
    Args:
        user: User object
        project: Project object  
        permissions: List of permission names
        
    Returns:
        Dict with permission names as keys and boolean results as values
    """
    results = {}
    
    if user == project.owner:
        # Owner has all permissions
        return {perm: True for perm in permissions}
    
    try:
        membership = project.memberships.get(user=user, is_active=True)
        if membership.is_expired():
            return {perm: False for perm in permissions}
        
        effective_perms = membership.get_effective_permissions()
        
        for perm in permissions:
            results[perm] = effective_perms.get(perm, False)
            
    except project.memberships.model.DoesNotExist:
        results = {perm: False for perm in permissions}
    
    return results


# Helper functions for common academic use cases
def add_lab_members_to_project(project, research_group, pi_role='admin', 
                              postdoc_role='editor', student_role='collaborator'):
    """
    Helper function to add lab members to a project with appropriate roles.
    
    This implements the academic hierarchy described in the documentation:
    - PI can see all lab projects (admin role)
    - Postdocs can edit their projects + shared ones (editor role)
    - Students can view supervisor's projects (collaborator role)
    """
    added_members = []
    
    for membership in research_group.researchgroupmembership_set.filter(is_active=True):
        user = membership.user
        group_role = membership.role
        
        # Skip if user is already the project owner
        if user == project.owner:
            continue
        
        # Determine project role based on group hierarchy
        if group_role in ['postdoc', 'researcher']:
            project_role = postdoc_role
        elif group_role in ['phd', 'masters', 'undergrad']:
            project_role = student_role
        elif group_role == 'visiting':
            project_role = 'viewer'
        elif group_role == 'collaborator':
            project_role = 'collaborator'
        else:
            project_role = student_role  # Default
        
        # Add member to project
        project_membership = project.add_collaborator(
            user=user,
            role=project_role,
            granted_by=project.owner
        )
        added_members.append(project_membership)
    
    # Add PI as admin if not owner
    if research_group.principal_investigator != project.owner:
        pi_membership = project.add_collaborator(
            user=research_group.principal_investigator,
            role=pi_role,
            granted_by=project.owner
        )
        added_members.append(pi_membership)
    
    # Add group admins as editors
    for admin in research_group.admins.all():
        if admin != project.owner:
            admin_membership = project.add_collaborator(
                user=admin,
                role='editor',
                granted_by=project.owner  
            )
            added_members.append(admin_membership)
    
    return added_members


def grant_temporary_reviewer_access(project, reviewer_email, duration_days=30):
    """
    Grant temporary reviewer access for external collaborators.
    
    This supports the use case: "Reviewers get temporary read access"
    """
    from django.contrib.auth.models import User
    from datetime import timedelta
    from django.utils import timezone
    
    try:
        reviewer = User.objects.get(email=reviewer_email)
    except User.DoesNotExist:
        # Could create a temporary user account here
        return None
    
    # Set expiration date
    expires_at = timezone.now() + timedelta(days=duration_days)
    
    # Add reviewer with limited permissions
    membership = project.add_collaborator(
        user=reviewer,
        role='reviewer',
        granted_by=project.owner,
        access_expires_at=expires_at,
        can_read_files=True,
        can_write_files=False,
        can_delete_files=False,
        can_export_data=False,  # Reviewers typically shouldn't export
        can_view_results=True
    )
    
    return membership