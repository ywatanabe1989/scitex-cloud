from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import UserProfile, APIKey

User = get_user_model()


@login_required
def profile_view(request):
    """User profile view."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Gather resource allocation statistics
    from apps.project_app.models import Project, RemoteCredential
    from apps.code_app.models import ProjectService
    from django.db.models import Sum, Q
    import os
    from pathlib import Path

    # Project statistics
    total_projects = Project.objects.filter(owner=request.user).count()
    local_projects = Project.objects.filter(owner=request.user, project_type='local').count()
    remote_projects = Project.objects.filter(owner=request.user, project_type='remote').count()

    # Remote credentials
    remote_credentials_count = RemoteCredential.objects.filter(user=request.user, is_active=True).count()

    # Active services (TensorBoard, Jupyter, etc.)
    active_services = ProjectService.objects.filter(
        user=request.user,
        status__in=['starting', 'running']
    ).count()

    # SSH keys count
    workspace_ssh_keys = request.user.ssh_public_keys.filter(key_type='workspace').count()
    git_ssh_keys = request.user.ssh_public_keys.filter(key_type='git').count()
    total_ssh_keys = workspace_ssh_keys + git_ssh_keys

    # Storage usage calculation
    total_storage_bytes = 0
    try:
        # Calculate storage for local projects
        for project in Project.objects.filter(owner=request.user, project_type='local'):
            project_path = Path(project.git_clone_path) if hasattr(project, 'git_clone_path') and project.git_clone_path else None
            if project_path and project_path.exists():
                # Calculate directory size recursively
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            if os.path.exists(file_path):
                                total_storage_bytes += os.path.getsize(file_path)
                        except (OSError, FileNotFoundError):
                            pass
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error calculating storage usage: {e}")

    # Convert bytes to human-readable format
    def human_readable_size(bytes_size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"

    storage_used = human_readable_size(total_storage_bytes)

    # Collaborations
    total_collaborations = Project.objects.filter(collaborators=request.user).count()

    context = {
        "profile": profile,
        "resources": {
            "total_projects": total_projects,
            "local_projects": local_projects,
            "remote_projects": remote_projects,
            "remote_credentials": remote_credentials_count,
            "active_services": active_services,
            "total_ssh_keys": total_ssh_keys,
            "workspace_ssh_keys": workspace_ssh_keys,
            "git_ssh_keys": git_ssh_keys,
            "storage_used": storage_used,
            "storage_bytes": total_storage_bytes,
            "total_collaborations": total_collaborations,
        }
    }

    return render(request, "accounts_app/profile.html", context)


@login_required
def profile_edit(request):
    """Edit user profile (GitHub-style settings page)."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Update user basic info
        request.user.first_name = request.POST.get("first_name", "").strip()
        request.user.last_name = request.POST.get("last_name", "").strip()
        request.user.email = request.POST.get("email", "").strip()
        request.user.save()

        # Update profile info
        profile.bio = request.POST.get("bio", "").strip()
        profile.location = request.POST.get("location", "").strip()
        profile.timezone = request.POST.get("timezone", "").strip() or "UTC"
        profile.institution = request.POST.get("institution", "").strip()
        profile.website = request.POST.get("website", "").strip()
        profile.orcid = request.POST.get("orcid", "").strip()
        profile.google_scholar = request.POST.get("google_scholar", "").strip()
        profile.twitter = request.POST.get("twitter", "").strip()

        # Handle avatar upload
        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]

        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("accounts_app:profile_edit")

    context = {
        "profile": profile,
        "user": request.user,
    }

    return render(request, "accounts_app/profile_edit.html", context)


@login_required
def appearance_settings(request):
    """Appearance settings page (GitHub-style /settings/appearance)."""
    context = {
        "user": request.user,
    }
    return render(request, "accounts_app/appearance_settings.html", context)


@login_required
def ssh_keys(request):
    """SSH key management page."""
    from apps.project_app.services.ssh_service import SSHKeyManager
    from apps.project_app.services.gitea_sync_service import (
        sync_ssh_key_to_gitea,
        remove_ssh_key_from_gitea,
    )
    from apps.accounts_app.models import WorkspaceSSHKey
    from apps.accounts_app.utils.ssh_key_validator import SSHKeyValidator

    ssh_manager = SSHKeyManager(request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        # Git SSH key actions
        if action == "generate":
            success, public_key, error = ssh_manager.get_or_create_user_key()
            if success:
                messages.success(request, "SSH key generated successfully!")

                # Sync SSH key to Gitea
                sync_success, sync_error = sync_ssh_key_to_gitea(request.user)
                if sync_success:
                    messages.success(
                        request, "SSH key synced to Gitea - you can now use SSH clone!"
                    )
                else:
                    messages.warning(
                        request,
                        f"SSH key created but Gitea sync failed: {sync_error}. You may need to add the key manually to Gitea.",
                    )
            else:
                messages.error(request, f"Failed to generate SSH key: {error}")

        elif action == "delete":
            success, error = ssh_manager.delete_user_key()
            if success:
                messages.success(request, "SSH key deleted successfully!")

                # Remove SSH key from Gitea
                remove_success, remove_error = remove_ssh_key_from_gitea(request.user)
                if remove_success:
                    messages.success(request, "SSH key removed from Gitea")
                else:
                    messages.warning(
                        request,
                        f"SSH key deleted locally but Gitea removal failed: {remove_error}",
                    )
            else:
                messages.error(request, f"Failed to delete SSH key: {error}")

        # Workspace SSH key actions
        elif action == "add_workspace_key":
            title = request.POST.get("title", "").strip()
            public_key = request.POST.get("public_key", "").strip()
            sync_to_gitea = request.POST.get("sync_to_gitea") == "on"

            if not title or not public_key:
                messages.error(request, "Both title and public key are required")
            else:
                # Validate SSH key
                result = SSHKeyValidator.validate_and_parse(public_key)

                if not result["valid"]:
                    messages.error(request, f"Invalid SSH key: {result['error']}")
                else:
                    # Check for duplicate fingerprint
                    if WorkspaceSSHKey.objects.filter(
                        user=request.user, fingerprint=result["fingerprint"]
                    ).exists():
                        messages.error(
                            request, "This SSH key is already registered to your account"
                        )
                    else:
                        # Create new workspace SSH key
                        workspace_key = WorkspaceSSHKey.objects.create(
                            user=request.user,
                            title=title,
                            public_key=result["formatted_key"],
                            fingerprint=result["fingerprint"],
                            key_type=result["key_type"],
                        )
                        messages.success(
                            request,
                            f'SSH key "{title}" added successfully! You can now use it to connect to your workspace.',
                        )

                        # Optionally sync to Gitea
                        if sync_to_gitea:
                            from apps.gitea_app.api_client import GiteaClient, GiteaAPIError

                            try:
                                client = GiteaClient()
                                # Check if key already exists in Gitea by fingerprint
                                existing_key = client.find_ssh_key_by_fingerprint(
                                    result["fingerprint"].replace("SHA256:", ""),
                                    request.user.username,
                                )

                                if not existing_key:
                                    client.add_ssh_key(
                                        title=f"{title} (Workspace Key)",
                                        key=result["formatted_key"],
                                        username=request.user.username,
                                    )
                                    messages.success(
                                        request,
                                        f'SSH key also synced to Gitea! You can now use it for: git clone ssh://git@127.0.0.1:2222/...',
                                    )
                                else:
                                    messages.info(
                                        request, "SSH key already exists in Gitea - no sync needed"
                                    )
                            except Exception as e:
                                messages.warning(
                                    request,
                                    f"Workspace key added but Gitea sync failed: {str(e)}. You can add it manually in Gitea.",
                                )

        elif action == "delete_workspace_key":
            key_id = request.POST.get("key_id")
            try:
                key = WorkspaceSSHKey.objects.get(id=key_id, user=request.user)
                key_title = key.title
                key.delete()
                messages.success(request, f'SSH key "{key_title}" deleted successfully!')
            except WorkspaceSSHKey.DoesNotExist:
                messages.error(request, "SSH key not found")

        # Remote credential actions
        elif action == "add_remote_credential":
            from apps.project_app.models import RemoteCredential
            from pathlib import Path
            import subprocess
            import tempfile

            name = request.POST.get("name", "").strip()
            ssh_host = request.POST.get("ssh_host", "").strip()
            ssh_port = request.POST.get("ssh_port", "22").strip()
            ssh_username = request.POST.get("ssh_username", "").strip()
            ssh_public_key = request.POST.get("ssh_public_key", "").strip()

            if not all([name, ssh_host, ssh_username, ssh_public_key]):
                messages.error(request, "All fields are required for remote credentials")
            else:
                try:
                    ssh_port = int(ssh_port)
                except ValueError:
                    messages.error(request, "Invalid SSH port number")
                    return redirect("accounts_app:ssh_keys")

                # Generate SSH key fingerprint
                try:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pub') as f:
                        f.write(ssh_public_key)
                        temp_pub_path = f.name

                    result = subprocess.run(
                        ['ssh-keygen', '-lf', temp_pub_path],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    fingerprint = result.stdout.split()[1] if result.stdout else "Unknown"
                    Path(temp_pub_path).unlink()

                except Exception as e:
                    messages.error(request, f"Invalid SSH public key: {str(e)}")
                    return redirect("accounts_app:ssh_keys")

                private_key_path = f"/home/{request.user.username}/.ssh/scitex_remote_{name.lower().replace(' ', '_')}"

                try:
                    RemoteCredential.objects.create(
                        user=request.user,
                        name=name,
                        ssh_host=ssh_host,
                        ssh_port=ssh_port,
                        ssh_username=ssh_username,
                        ssh_public_key=ssh_public_key,
                        ssh_key_fingerprint=fingerprint,
                        private_key_path=private_key_path,
                        is_active=True
                    )
                    messages.success(
                        request,
                        f"Remote credential '{name}' added successfully! "
                        f"Please ensure your private key is at: {private_key_path}"
                    )
                except Exception as e:
                    messages.error(request, f"Failed to add credential: {str(e)}")

        elif action == "delete_remote_credential":
            from apps.project_app.models import RemoteCredential

            credential_id = request.POST.get("credential_id")
            try:
                credential = RemoteCredential.objects.get(id=credential_id, user=request.user)
                credential_name = credential.name
                credential.delete()
                messages.success(request, f"Remote credential '{credential_name}' deleted")
            except RemoteCredential.DoesNotExist:
                messages.error(request, "Credential not found")

        elif action == "test_remote_credential":
            from apps.project_app.models import RemoteCredential
            import subprocess

            credential_id = request.POST.get("credential_id")
            try:
                credential = RemoteCredential.objects.get(id=credential_id, user=request.user)
                ssh_key_path = credential.private_key_path

                cmd = [
                    "ssh",
                    "-p", str(credential.ssh_port),
                    "-i", ssh_key_path,
                    "-o", "StrictHostKeyChecking=accept-new",
                    "-o", "ConnectTimeout=10",
                    f"{credential.ssh_username}@{credential.ssh_host}",
                    "echo 'OK'"
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

                if result.returncode == 0:
                    messages.success(request, f"✅ Connection successful to {credential.name}")
                else:
                    messages.error(request, f"❌ Connection failed to {credential.name}: {result.stderr}")

            except RemoteCredential.DoesNotExist:
                messages.error(request, "Credential not found")
            except subprocess.TimeoutExpired:
                messages.error(request, "Connection timeout")
            except Exception as e:
                messages.error(request, f"Connection test failed: {str(e)}")

        return redirect("accounts_app:ssh_keys")

    # GET request
    workspace_ssh_keys = WorkspaceSSHKey.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    # Get remote credentials
    from apps.project_app.models import RemoteCredential
    remote_credentials = RemoteCredential.objects.filter(user=request.user).order_by(
        '-last_used_at', '-created_at'
    )

    context = {
        # Git SSH keys
        "ssh_public_key": profile.ssh_public_key,
        "ssh_key_fingerprint": profile.ssh_key_fingerprint,
        "ssh_key_created_at": profile.ssh_key_created_at,
        "ssh_key_last_used_at": profile.ssh_key_last_used_at,
        "has_ssh_key": ssh_manager.has_ssh_key(),
        # Workspace SSH keys
        "workspace_ssh_keys": workspace_ssh_keys,
        # Remote credentials
        "remote_credentials": remote_credentials,
    }
    return render(request, "accounts_app/ssh_keys.html", context)


@login_required
def api_keys(request):
    """API key management page."""
    user_api_keys = APIKey.objects.filter(user=request.user).select_related("user")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            name = request.POST.get("name", "").strip()
            scopes = request.POST.getlist("scopes")

            if not name:
                messages.error(request, "API key name is required")
            else:
                api_key_obj, full_key = APIKey.create_key(
                    user=request.user,
                    name=name,
                    scopes=scopes or ["*"],  # Default: full access
                )
                # Store the full key in session to show once
                request.session["new_api_key"] = full_key
                request.session["new_api_key_name"] = name
                messages.success(request, f'API key "{name}" created successfully!')

        elif action == "delete":
            key_id = request.POST.get("key_id")
            try:
                api_key = APIKey.objects.get(id=key_id, user=request.user)
                key_name = api_key.name
                api_key.delete()
                messages.success(request, f'API key "{key_name}" deleted successfully!')
            except APIKey.DoesNotExist:
                messages.error(request, "API key not found")

        elif action == "toggle":
            key_id = request.POST.get("key_id")
            try:
                api_key = APIKey.objects.get(id=key_id, user=request.user)
                api_key.is_active = not api_key.is_active
                api_key.save()
                status = "activated" if api_key.is_active else "deactivated"
                messages.success(request, f'API key "{api_key.name}" {status}')
            except APIKey.DoesNotExist:
                messages.error(request, "API key not found")

        return redirect("accounts_app:api_keys")

    # Get newly created key from session (show once)
    new_api_key = request.session.pop("new_api_key", None)
    new_api_key_name = request.session.pop("new_api_key_name", None)

    context = {
        "api_keys": user_api_keys,
        "new_api_key": new_api_key,
        "new_api_key_name": new_api_key_name,
    }
    return render(request, "accounts_app/api_keys.html", context)


# API Endpoints
@login_required
@require_http_methods(["POST"])
def api_generate_ssh_key(request):
    """API endpoint to generate SSH key."""
    from apps.project_app.services.ssh_service import SSHKeyManager
    from apps.project_app.services.gitea_sync_service import sync_ssh_key_to_gitea

    ssh_manager = SSHKeyManager(request.user)
    success, public_key, error = ssh_manager.get_or_create_user_key()

    if success:
        # Sync SSH key to Gitea
        sync_success, sync_error = sync_ssh_key_to_gitea(request.user)

        return JsonResponse(
            {
                "success": True,
                "public_key": public_key,
                "gitea_synced": sync_success,
                "gitea_error": sync_error,
            }
        )
    else:
        return JsonResponse({"success": False, "error": error}, status=400)


@login_required
def git_integrations(request):
    """Git Platform Integration settings page."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Update Git platform tokens
        github_token = request.POST.get("github_token", "").strip()
        gitlab_token = request.POST.get("gitlab_token", "").strip()
        bitbucket_token = request.POST.get("bitbucket_token", "").strip()

        if github_token:
            profile.github_token = github_token
        if gitlab_token:
            profile.gitlab_token = gitlab_token
        if bitbucket_token:
            profile.bitbucket_token = bitbucket_token

        # Update Git hosting profiles (public usernames)
        profile.github_profile = request.POST.get("github_profile", "").strip()
        profile.gitlab_profile = request.POST.get("gitlab_profile", "").strip()
        profile.bitbucket_profile = request.POST.get("bitbucket_profile", "").strip()

        profile.save()
        messages.success(request, "Git platform integrations updated successfully!")
        return redirect("accounts_app:git_integrations")

    # Helper function to mask tokens
    def mask_token(token):
        if not token or len(token) < 8:
            return None
        return f"{token[:4]}...{token[-4:]}"

    context = {
        "profile": profile,
        "github_token_masked": mask_token(profile.github_token)
        if profile.github_token
        else None,
        "gitlab_token_masked": mask_token(profile.gitlab_token)
        if profile.gitlab_token
        else None,
        "bitbucket_token_masked": mask_token(profile.bitbucket_token)
        if profile.bitbucket_token
        else None,
    }
    return render(request, "accounts_app/git_integrations.html", context)


@login_required
def account_settings(request):
    """Account settings page (email, password, delete account)."""
    from django.contrib.auth import update_session_auth_hash

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "change_email":
            new_email = request.POST.get("new_email", "").strip()
            if new_email:
                if (
                    User.objects.filter(email=new_email)
                    .exclude(pk=request.user.pk)
                    .exists()
                ):
                    messages.error(
                        request, "This email is already in use by another account."
                    )
                else:
                    # Send verification code to new email
                    from apps.auth_app.models import EmailVerification
                    from apps.project_app.services.email_service import EmailService
                    import secrets

                    # Store current email and pending new email in session
                    request.session["pending_email_change"] = {
                        "current_email": request.user.email,
                        "new_email": new_email,
                        "user_id": request.user.id,
                    }

                    # Generate and send OTP
                    otp_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
                    EmailVerification.objects.create(email=new_email, otp_code=otp_code)

                    try:
                        EmailService.send_verification_email(new_email, otp_code)
                        messages.success(
                            request,
                            f"Verification code sent to {new_email}. Please check your inbox.",
                        )
                        return redirect(
                            f"/auth/verify-email/?email={new_email}&type=email_change"
                        )
                    except Exception as e:
                        messages.error(
                            request, f"Failed to send verification email: {str(e)}"
                        )
            else:
                messages.error(request, "Please enter a valid email address.")

        elif action == "change_password":
            current_password = request.POST.get("current_password", "")
            new_password = request.POST.get("new_password", "")
            confirm_password = request.POST.get("confirm_password", "")

            if not request.user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            elif len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Keep user logged in
                messages.success(request, "Password updated successfully!")

        return redirect("accounts_app:account")

    context = {
        "user": request.user,
    }
    return render(request, "accounts_app/account_settings.html", context)


@login_required
def remote_credentials(request):
    """Remote credentials management page."""
    from apps.project_app.models import RemoteCredential
    from pathlib import Path
    import subprocess

    credentials = RemoteCredential.objects.filter(user=request.user).order_by('-last_used_at', '-created_at')

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            # Add new remote credential
            name = request.POST.get("name", "").strip()
            ssh_host = request.POST.get("ssh_host", "").strip()
            ssh_port = request.POST.get("ssh_port", "22").strip()
            ssh_username = request.POST.get("ssh_username", "").strip()
            ssh_public_key = request.POST.get("ssh_public_key", "").strip()

            # Validate inputs
            if not all([name, ssh_host, ssh_username, ssh_public_key]):
                messages.error(request, "All fields are required")
                return redirect("accounts_app:remote_credentials")

            try:
                ssh_port = int(ssh_port)
            except ValueError:
                messages.error(request, "Invalid SSH port number")
                return redirect("accounts_app:remote_credentials")

            # Generate SSH key fingerprint
            try:
                # Save public key to temp file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pub') as f:
                    f.write(ssh_public_key)
                    temp_pub_path = f.name

                # Get fingerprint
                result = subprocess.run(
                    ['ssh-keygen', '-lf', temp_pub_path],
                    capture_output=True,
                    text=True,
                    check=True
                )

                # Parse fingerprint (format: "2048 SHA256:xxx... user@host (RSA)")
                fingerprint = result.stdout.split()[1] if result.stdout else "Unknown"

                # Clean up temp file
                Path(temp_pub_path).unlink()

            except Exception as e:
                messages.error(request, f"Invalid SSH public key: {str(e)}")
                return redirect("accounts_app:remote_credentials")

            # Generate private key path (we don't store the private key, just reference it)
            private_key_path = f"/home/{request.user.username}/.ssh/scitex_remote_{name.lower().replace(' ', '_')}"

            # Create credential
            try:
                credential = RemoteCredential.objects.create(
                    user=request.user,
                    name=name,
                    ssh_host=ssh_host,
                    ssh_port=ssh_port,
                    ssh_username=ssh_username,
                    ssh_public_key=ssh_public_key,
                    ssh_key_fingerprint=fingerprint,
                    private_key_path=private_key_path,
                    is_active=True
                )

                messages.success(
                    request,
                    f"Remote credential '{name}' added successfully! "
                    f"Please ensure your private key is at: {private_key_path}"
                )

            except Exception as e:
                messages.error(request, f"Failed to add credential: {str(e)}")

            return redirect("accounts_app:remote_credentials")

        elif action == "delete":
            # Delete credential
            credential_id = request.POST.get("credential_id")

            try:
                credential = RemoteCredential.objects.get(id=credential_id, user=request.user)
                credential_name = credential.name
                credential.delete()
                messages.success(request, f"Remote credential '{credential_name}' deleted")

            except RemoteCredential.DoesNotExist:
                messages.error(request, "Credential not found")

            return redirect("accounts_app:remote_credentials")

        elif action == "test":
            # Test connection
            credential_id = request.POST.get("credential_id")

            try:
                credential = RemoteCredential.objects.get(id=credential_id, user=request.user)

                # Test SSH connection
                ssh_key_path = credential.private_key_path

                cmd = [
                    "ssh",
                    "-p", str(credential.ssh_port),
                    "-i", ssh_key_path,
                    "-o", "StrictHostKeyChecking=accept-new",
                    "-o", "ConnectTimeout=10",
                    f"{credential.ssh_username}@{credential.ssh_host}",
                    "echo 'OK'"
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=15
                )

                if result.returncode == 0:
                    messages.success(request, f"✅ Connection successful to {credential.name}")
                else:
                    messages.error(
                        request,
                        f"❌ Connection failed to {credential.name}: {result.stderr}"
                    )

            except RemoteCredential.DoesNotExist:
                messages.error(request, "Credential not found")
            except subprocess.TimeoutExpired:
                messages.error(request, "Connection timeout")
            except Exception as e:
                messages.error(request, f"Connection test failed: {str(e)}")

            return redirect("accounts_app:remote_credentials")

    context = {
        "credentials": credentials,
    }

    return render(request, "accounts_app/remote_credentials.html", context)
