# Instance setup
```
sudo yum update -y
sudo yum install nginx -y
sudo yum install git -y
sudo mkdir www
sudo mkdir github
sudo yum install python311
sudo yum install python-devel
sudo yum install sqlite
sudo yum install nodejs
```

add credentials to github account: 

sudo yum groupinstall "Development Tools"

Deploying a Django and React application on AWS Linux involves configuring Nginx as a reverse proxy and Gunicorn as an application server. Here's a guide to achieve this: 

• Set up an EC2 instance: Launch an AWS EC2 instance with Linux. Connect to it via SSH. 
• Install necessary packages: Update the system packages and install Python, pip, Nginx, and Gunicorn. 

sudo yum update -y
sudo yum install python3 python3-pip nginx
pip3 install virtualenv

• Create a virtual environment: Create a virtual environment for the Django project and activate it. 

python3 -m virtualenv venv
source venv/bin/activate

• Install project dependencies: Upload the Django project files to the instance and install the required Python packages. 

pip3 install -r requirements.txt

• Configure Gunicorn: Test Gunicorn's ability to serve the Django project. 

gunicorn --bind 0.0.0.0:8000 your_project.wsgi

• Create systemd service files: Configure Gunicorn to run as a systemd service. Create a socket and a service file for Gunicorn. 

# /etc/systemd/system/gunicorn.socket
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target

# /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/project/venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock your_project.wsgi
RuntimeDirectory=run
[Install]
WantedBy=multi-user.target

• Start Gunicorn: Enable and start the Gunicorn socket and service. 

sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl start gunicorn.service
sudo systemctl enable gunicorn.service

• Configure Nginx: Configure Nginx to act as a reverse proxy, forwarding requests to Gunicorn. 

# /etc/nginx/nginx.conf
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /path/to/your/project/static/;
    }
}

• Restart Nginx: Restart Nginx to apply the changes. 

sudo systemctl restart nginx

• React build: Build the React application and place the build output in the appropriate directory (e.g., static folder). 
• Security: Configure security groups on AWS to allow traffic on port 80 (HTTP) and 443 (HTTPS). Consider using a firewall for additional security. 
• Testing: Access the application through the browser using the EC2 instance's public IP or domain name. 


Generative AI is experimental.

[-] https://stackoverflow.com/questions/67272648/failed-to-start-gunicorn-service-job-for-gunicorn-socket-failed-ubunto-18-04[-] https://selectel.ru/blog/tutorials/django-blog-2/[-] https://stackoverflow.com/questions/39262172/flask-nginx-url-for-external
