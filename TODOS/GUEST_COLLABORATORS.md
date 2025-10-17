# Guest Collaborator System - Email-Based Limited Access

## Problem
Professors/reviewers don't want to create accounts just to review a manuscript.

## Solution: Token-Based Guest Access

### Workflow
1. **Owner invites by email** (no account needed)
   ```
   "Add Collaborator" → Enter email → Send invite
   ```

2. **Guest receives email** with magic link
   ```
   Subject: You've been invited to review "Paper Title"
   Link: https://scitex.ai/writer/guest/abc123token456
   Valid for: 7 days
   ```

3. **Guest accesses via token**
   - No login required
   - Limited to specific manuscript
   - Read + comment permissions
   - Optional: Suggest changes

### Guest Permissions (Limited)

**Can Do:**
- ✅ View manuscript (read-only)
- ✅ View compiled PDF
- ✅ Add comments/suggestions
- ✅ Export PDF
- ✅ View change history

**Cannot Do:**
- ❌ Edit text directly
- ❌ Delete content
- ❌ Invite others
- ❌ Access other projects
- ❌ See user's other manuscripts

### Models Needed

```python
class GuestCollaborator(models.Model):
    """Guest access for reviewers without accounts."""
    manuscript = ForeignKey(Manuscript)
    email = EmailField()
    invited_by = ForeignKey(User)
    
    # Access token
    access_token = CharField(max_length=64, unique=True)  # UUID
    
    # Permissions
    can_comment = BooleanField(default=True)
    can_suggest_changes = BooleanField(default=False)
    can_download_pdf = BooleanField(default=True)
    
    # Status
    is_active = BooleanField(default=True)
    expires_at = DateTimeField()  # Default: 7 days
    first_accessed_at = DateTimeField(null=True)
    last_accessed_at = DateTimeField(null=True)
    access_count = IntegerField(default=0)
    
    # Guest info (collected on first access)
    guest_name = CharField(max_length=200, blank=True)
    affiliation = CharField(max_length=500, blank=True)
    
    created_at = DateTimeField(auto_now_add=True)
```

### Implementation

**Backend:**
1. Generate unique token (UUID)
2. Send email with magic link
3. Validate token on access
4. Track usage and expiration

**Frontend:**
- Guest sees read-only view with comment sidebar
- "Sign up to edit directly" banner
- Limited UI (no edit buttons)

### Benefits

**For Owners:**
- Easy to share for review
- No "create an account" friction
- Trackable (who accessed when)
- Revocable access

**For Guests:**
- One-click access
- No password to remember
- Professional reviewer experience
- Can upgrade to full account later

### Security

- Token is cryptographically random (64 chars)
- Expires after 7 days
- Can be revoked anytime
- Rate limited (max 100 views per token)
- IP logging for abuse detection

### Email Template

```
Subject: Review Invitation: "{{manuscript.title}}"

Hi,

{{invited_by.name}} has invited you to review their manuscript:

"{{manuscript.title}}"

Click here to access: https://scitex.ai/writer/guest/{{token}}

This link is valid for 7 days and allows you to:
- Read the manuscript
- View the compiled PDF
- Leave comments and suggestions

No account required!

---
The SciTeX Team
```

### URLs

```
/writer/guest/<token>/ - Guest access view
/writer/guest/<token>/pdf/ - PDF download
/writer/guest/<token>/comment/ - Add comment (POST)
```

### Priority

**HIGH** - This is a killer feature for academic collaboration!

Professors are busy - removing signup friction = more reviews = better papers.

### Implementation Time

**2-3 days:**
- Day 1: Model, token generation, email sending
- Day 2: Guest view UI, comment system
- Day 3: Testing, polish

### Alternative: Just Share Link?

Could also support:
```
/username/project/blob/paper/manuscript.pdf?share=abc123
```

But dedicated guest system is better because:
- Can track who viewed
- Can add comments
- Can expire access
- More professional

---

Recommend implementing this before Phase 3 (Track Changes) since it's:
- High value for users
- Relatively simple
- Enables real-world testing of collaboration features

