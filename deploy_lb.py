import os
import subprocess

def install_web_server_and_certificate(email, domain):
    # Install Apache web server
    subprocess.run(["sudo", "apt-get", "install", "-y", "apache2"])

    # Install Certbot for Let's Encrypt
    subprocess.run(["sudo", "apt-get", "install", "-y", "certbot", "python3-certbot-apache"])

    # Obtain SSL certificate
    subprocess.run(["sudo", "certbot", "--apache", "--agree-tos", "--no-eff-email", "-m", email, "-d", domain])

    # Configure Apache virtual host
    with open(f"/etc/apache2/sites-available/{domain}.conf", "w") as f:
        f.write(f"""
    <VirtualHost *:80>
        ServerName {domain}
        ServerAlias www.{domain}
        Redirect permanent / https://{domain}/
    </VirtualHost>

    <VirtualHost *:443>
        ServerName {domain}
        ServerAlias www.{domain}
        DocumentRoot /var/www/{domain}
        ErrorLog ${{{APACHE_LOG_DIR}}}/error.log
        CustomLog ${{{APACHE_LOG_DIR}}}/access.log combined
        SSLEngine on
        SSLCertificateFile /etc/letsencrypt/live/{domain}/fullchain.pem
        SSLCertificateKeyFile /etc/letsencrypt/live/{domain}/privkey.pem
    </VirtualHost>
    """)

    # Enable virtual host and SSL module
    subprocess.run(["sudo", "a2ensite", f"{domain}.conf"])
    subprocess.run(["sudo", "a2enmod", "ssl"])

    # Restart Apache
    subprocess.run(["sudo", "systemctl", "restart", "apache2"])

# Usage
install_web_server_and_certificate("your-email@example.com", "your-domain.com")
