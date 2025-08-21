# Instance setup

## For RHEL/CentOS/Rocky/Amazon Linux
```
sudo dnf update -y
sudo dnf install -y \
    nginx \
    git \
    nodejs \
    postgresql-server
```

## Configure postgresql server
sudo -u postgres psql

ALTER USER postgres WITH PASSWORD 'SUPER_SECRET_PASSWORD';
CREATE DATABASE 'ictsdashboard_app';
\q

* Open firewall port for postgresql-server for localhost processes only
sudo firewalld-cmd --permanent --zone=trusted --add-service=postgresql
sudo firewalld-cmd --reload

## Configure Git
add credentials to github account with:
  `$ git config --global user.name "Your-GitHub-Username" user.email "Your-Email-Address"`

## Make the repo working directory, set user-level write permissions and pull the repo:
sudo mkdir -p /var/www/github
sudo chown {Your-username}:{Your-groupname} /var/www/github

cd /var/www/github
git clone git@github.com:UCI-ICTS/icts-dashboard.git`

## Install [pyenv](https://github.com/pyenv/pyenv)

## [Set up pyenv build environment](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
• This is required for installing python through pyenv

### If using RHEL, you will need to add the [EPEL](https://www.redhat.com/en/blog/install-epel-linux) repos to install "Developemnt Tools"
```
sudo dnf groupinstall "Development Tools"
```

## Install project-specific python 3.11
pyenv install 3.11.13
pyenv local 3.11.13

## Set up icts-dashboard python environment and install project dependencies
cd /var/www/github/icts-dashboard/server

python -m virtualenv env
source env/bin/activate
pip install -r requirements.txt

## Add nginx group access to pyenv and icts-dashboard binaries
sudo chown :nginx $HOME/versions/3.11.13/bin/*
sudo chown :nginx /var/www/github/icts-dashboard/server/env/bin/*

## Configure .secrets for postgresql connection
cp .secrets.example .secrets
* Create a new Django secret key and save it to the [DJANGO_KEYS] SECRET_KEY line.
openssl rand -base64 32
* Configure the postgresql-server database name and login credentials to match those set earlier for the [DATABASE] NAME, USER, and PASSWORD fields.

## Make database migrations and load initial data for initial login
cd /var/www/github/icts-dashboard/server

python -m manage makemigrations
python -m manage migrate
python -m manage loaddata config/fixtures/initial.json

## Copy systemd socket and service files from `icts-dashboard/admin/`:
cd /var/www/github/icts-dashboard/admin/

sudo cp icts.socket /etc/systemd/system/
sudo cp icts.service /etc/systemd/system/

## Create SELinux policies for pyenv and icts-dashboard binaries
sudo semanage fcontext -a -t bin_t "$HOME/.pyenv/versions/3.11.13/bin(/.*)?"
sudo restoreconf -vF $HOME/versions/3.11.13/bin/*"
sudo semanage fcontext -a -t bin_t "/var/www/github/icts-dashboard/server/env/bin(/.*)?"
sudo restoreconf -vF /var/www/github/icts-dashboard/server/env/bin/*

## Start Gunicorn: Enable and start the ICTS socket and service.
sudo systemctl start icts.socket
sudo systemctl enable icts.socket
sudo systemctl start icts.service
sudo systemctl enable icts.service

## Configure Nginx: Configure Nginx to act as a reverse proxy, forwarding requests to Gunicorn.
* Configure HTTPS with a self-signed certificate until a CA certificate is obtained.
sudo openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt

## Copy the nginx configuration
cd /var/www/github/icts-dashboard/admin

sudo cp icts.conf /etc/nginx/conf.d/

## Create SELinux policy for nginx config
sudo semanage fcontext -a -t httpd_config_t "/etc/nginx/conf.d/icts.conf"
sudo restoreconf -vF /etc/nginx/conf.d/icts.conf

## Open firewall ports for HTTP and HTTPS
sudo firewalld-cmd --permanent --zone=public --add-service=http
sudo firewalld-cmd --permanent --zone=public --add-service=https
sudo firewalld-cmd --reload

## Test nginx config and correct configuration errors
sudo nginx -t

## Start and enable nginx once there are no errors
sudo systemctl start nginx
sudo systemctl enable nginx

## Attempt to access the website from your web browser with HTTPS