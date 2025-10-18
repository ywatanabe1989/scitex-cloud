<!-- ---
!-- Timestamp: 2025-10-18 10:38:29
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/config/deployment/nginx/README.md
!-- --- -->

# Remove old symlink
sudo rm /etc/nginx/sites-enabled/scitex-https.conf
sudo rm /etc/nginx/sites-available/scitex-https.conf

# Create new symlink to your updated config
sudo ln -sfr /home/ywatanabe/proj/scitex-cloud/config/deployment/nginx/scitex-https.conf \
    /etc/nginx/sites-available/scitex-https.conf
sudo ln -sfr /etc/nginx/sites-available/scitex-https.conf /etc/nginx/sites-enabled/scitex-https.conf

# Test Nginx configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx

# Now start uWSGI (your server.sh currently starts Gunicorn, we need uWSGI instead)
# Check if you have a uwsgi config
ls -la /home/ywatanabe/proj/scitex-cloud/config/deployment/uwsgi/

<!-- EOF -->