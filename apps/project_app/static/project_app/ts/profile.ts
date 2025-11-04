// =============================================================================
// User Profile Functions
// =============================================================================

// Simple client-side repository search
document.getElementById('repo-search')?.addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    const repoItems = document.querySelectorAll('.repo-item');

    repoItems.forEach(item => {
        const repoName = item.querySelector('.repo-name').textContent.toLowerCase();
        const repoDesc = item.querySelector('.repo-description')?.textContent.toLowerCase() || '';

        if (repoName.includes(searchTerm) || repoDesc.includes(searchTerm)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
});

// =============================================================================
// Follow/Unfollow Functionality
// =============================================================================

async function toggleFollow() {
    const btn = document.getElementById('follow-btn');
    const isFollowing = btn.innerHTML.includes('Following');

    const profileData = window.SCITEX_PROFILE_DATA;
    if (!profileData || !profileData.username) {
        console.error('Profile data not available');
        return;
    }

    const username = profileData.username;
    const endpoint = isFollowing
        ? `/social/api/unfollow/${username}/`
        : `/social/api/follow/${username}/`;

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            // Toggle button state
            if (isFollowing) {
                btn.innerHTML = '<i class="fas fa-user-plus"></i> Follow';
            } else {
                btn.innerHTML = '<i class="fas fa-user-check"></i> Following';
            }

            // Update follower count
            const followerCount = document.querySelector('.profile-stat strong');
            if (followerCount) {
                followerCount.textContent = data.followers_count;
            }
        } else {
            alert(data.error || 'Failed to update follow status');
        }
    } catch (err) {
        console.error('Follow error:', err);
        alert('Failed to update follow status');
    }
}

// =============================================================================
// Star/Unstar Repository Functionality
// =============================================================================

async function toggleStar(btn) {
    const isStarred = btn.innerHTML.includes('Unstar');
    const username = btn.dataset.username;
    const slug = btn.dataset.slug;

    const endpoint = isStarred
        ? `/social/api/unstar/${username}/${slug}/`
        : `/social/api/star/${username}/${slug}/`;

    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '⏳ ...';

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            // Get the static URL for star icon
            const starIconUrl = btn.dataset.starIcon || '/static/project_app/icons/star.svg';

            // Toggle button state
            if (isStarred) {
                btn.innerHTML = `<img src="${starIconUrl}" alt="" style="width: 14px; height: 14px; vertical-align: text-bottom; margin-right: 4px;">Star`;
            } else {
                btn.innerHTML = `<img src="${starIconUrl}" alt="" style="width: 14px; height: 14px; vertical-align: text-bottom; margin-right: 4px;">Unstar`;
            }
        } else {
            alert(data.error || 'Failed to update star status');
            btn.innerHTML = originalHTML;
        }
    } catch (err) {
        console.error('Star error:', err);
        alert('Failed to update star status');
        btn.innerHTML = originalHTML;
    } finally {
        btn.disabled = false;
    }
}

// =============================================================================
// Helper Functions
// =============================================================================

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
