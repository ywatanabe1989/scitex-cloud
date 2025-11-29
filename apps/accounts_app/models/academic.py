"""
Academic Institution Detection

Utilities for detecting Japanese academic email domains.
"""

# Japanese Academic domains to recognize
JAPANESE_ACADEMIC_DOMAINS = [
    # Japanese Academic (.ac.jp) - All academic institutions
    ".ac.jp",
    ".u-tokyo.ac.jp",
    ".kyoto-u.ac.jp",
    ".osaka-u.ac.jp",
    ".tohoku.ac.jp",
    ".nagoya-u.ac.jp",
    ".kyushu-u.ac.jp",
    ".hokudai.ac.jp",
    ".tsukuba.ac.jp",
    ".hiroshima-u.ac.jp",
    ".kobe-u.ac.jp",
    ".waseda.jp",
    ".keio.ac.jp",
    # Government Research Institutions (.go.jp)
    ".go.jp",  # Broader government research support
    ".riken.jp",
    ".aist.go.jp",
    ".nict.go.jp",
    ".jaxa.jp",
    ".jst.go.jp",
    ".nims.go.jp",
    ".nies.go.jp",
]


def is_japanese_academic_email(email):
    """Check if email belongs to Japanese academic institution"""
    if not email:
        return False
    try:
        domain = email.lower().split("@")[1]
        # Check if domain matches exactly or ends with the academic domain
        for academic_domain in JAPANESE_ACADEMIC_DOMAINS:
            # Remove leading dot for exact matching
            clean_domain = academic_domain.lstrip(".")
            if domain == clean_domain or domain.endswith(academic_domain):
                return True
        return False
    except (IndexError, AttributeError):
        return False
