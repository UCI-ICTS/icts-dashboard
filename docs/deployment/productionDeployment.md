# Dashboard Production Deployment

## System Setup
Install Required Dependencies
Run the following to install Python, PostgreSQL (or SQLite), NginX, and Gunicorn:

    sudo dnf install -y python3 python3-venv python3-pip git nginx policycoreutils-python-utils

## Clone the Repository 
    cd /var/www/github/
    git clone https://github.com/your-repo/GREGor_dashboard.git
    
## Dashboard Client deployment  (GREGor_dashboard/client)
    cd GREGor_dashboard/client

### Enter the repository, create a environment file, and install the required packages

	cd GREGor_dashboard/client/

**Install Node packages via Node Package Manager (NPM)**

	npm install

### Update the `.env` file with the required keys: 
	cp .env.example .env

The APIDB should be `icts8201.hs.uci.edu` for production.
```
REACT_APP_APIDB="https://icts8201.hs.uci.edu"
```

### **Build service**

`npm run build`

This will build a production ready deployment in  `GREGor_dashboard/client/build`  if everything goes according to plan. If not, see the [troubleshooting tips](troubleshooting.md).

This will be serving the React frontend.

## Configure Django Settings & Setup the Virtual Environment
    cd GREGor_dashboard/server
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt

### Create .secrets File 
    cp .secrets.example .secrets

### Edit the file to set production values
    vim .secrets  

```
[DJANGO_KEYS]
SECRET_KEY=[generate a key for this]

[SERVER]
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,icts8201.hs.uci.edu,genomics.icts.uci.edu
SERVER_VERSION=[version of app on Git]
DASHBOARD_URL=https://icts8201.hs.uci.edu
DATABASE=db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
SCHEMA_VERSION=[GREGoR schema version]
```

### Set Database Migrations
    python manage.py migrate
### Create an admin user (follow prompts)
    python manage.py createsuperuser  

### Collect Static Files
    python manage.py collectstatic

📌 Note: If permission is denied, ensure STATIC_ROOT is correctly set in settings.py and that the directory is writable.

### Set Permissions for Database & Static Files

    sudo chown -R dashboard:developers /var/www/github/GREGor_dashboard/server/db.sqlite3
    sudo chmod 664 /var/www/github/GREGor_dashboard/server/db.sqlite3
    sudo chown -R dashboard:developers /var/www/github/GREGor_dashboard/server/static
    sudo chmod -R 775 /var/www/github/GREGor_dashboard/server/static

### Configure Gunicorn
Look at `GREGor_dashboard/admin/gregor.service`. It should look like this:
```shell
Description=GREGoR Dashboard gunicorn daemon
After=network.target

[Service]
User=dashboard
Group=developers
WorkingDirectory=/var/www/github/GREGor_dashboard/server
ExecStart=/var/www/github/GREGor_dashboard/server/env/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/run/gregor.sock \
    config.wsgi:application
Restart=always
Environment="PATH=/var/www/github/GREGor_dashboard/server/env/bin"

[Install]
WantedBy=multi-user.target
```

#### if it does, create gregor.service for Gunicorn

    sudo cp /var/www/github/GREGor_dashboard/admin/gregor.service /etc/systemd/system/gregor.service


### Enable and Start Gunicorn
    sudo systemctl daemon-reload
    sudo systemctl enable gregor
    sudo systemctl start gregor
#### Verify Gunicorn is running
    sudo systemctl status gregor  

## Configure NginX
### Verify or Edit NginX Configuration
Look at `GREGor_dashboard/admin/prd_gregor.conf`. It should look like this:

```shell
server {
    listen 443 ssl;
    server_name icts8201.hs.uci.edu;

    ssl_certificate /etc/ssl/certs/icts8201_fullchain.pem;
    ssl_certificate_key /etc/ssl/private/icts8201_private.key;

    # Enable HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    location /api/static/ {
        alias /var/www/github/GREGor_dashboard/server/static/;
        autoindex on;
    }

    location /api/ {
        proxy_pass http://unix:/var/run/gregor.sock;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### if it does:

    sudo cp  /var/www/github/GREGor_dashboard/admin/gregor.service /etc/nginx/conf.d/gregor.conf

### Test and Restart NginX
    sudo nginx -t  # Test for syntax errors
    sudo systemctl restart nginx

## Configure SELinux
### Allow NginX to Connect to Gunicorn
    sudo setsebool -P httpd_can_network_connect on
    sudo setsebool -P httpd_can_network_relay on

### Ensure NginX Can Access the Socket
    sudo semanage fcontext -a -t httpd_var_run_t "/var/run/gregor.sock"
    sudo restorecon -v /var/run/gregor.sock
    sudo chown nginx:developers /var/run/gregor.sock
    sudo chmod 660 /var/run/gregor.sock

### Create a Custom SELinux Policy for NginX
    sudo ausearch -m AVC,USER_AVC -c nginx --raw | audit2allow -M nginx_gunicorn
    sudo semodule -i nginx_gunicorn.pp
## Verify Deployment
Test API Endpoint:

    curl -X GET https://icts8201.hs.uci.edu/api/admin/ -H "Content-Type: application/json"

✅ Expected Output: Nothing confirms the server is running.

### Check Logs If Issues Occur
    sudo journalctl -u gregor --no-pager | tail -20
    sudo tail -f /var/log/nginx/error.log

## 🔁 Maintenance & Updates
### Restart Services After Changes
    sudo systemctl restart gregor
    sudo systemctl restart nginx
### Backup SELinux Configuration
Run:

    sh /var/www/github/GREGor_dashboard/server/utilities/selinux_snapshot.sh

The snapshot will be stored in: `/var/www/github/GREGor_dashboard/admin/SELinux_Full_Snapshot.txt`

### Pulling New Changes From GitHub
    cd /var/www/github/GREGor_dashboard/
    git pull origin main

#### Then restart:
    sudo systemctl restart gregor
    sudo systemctl restart nginx


If any other issues arise, refer to:

    sudo journalctl -u gregor --no-pager | tail -20

or 

    sudo tail -f /var/log/nginx/error.log