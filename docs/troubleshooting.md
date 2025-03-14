# Troubleshooting Tips for GREGoR Dashboard Deployment

This document provides a list of common issues and steps to resolve them during the production deployment of the GREGoR Dashboard using Django, Gunicorn, NginX, and SELinux.

---

## 1. Gunicorn and Virtual Environment Issues

### **ModuleNotFoundError: No module named 'gunicorn'**
- **Cause:** Gunicorn is not installed in the virtual environment.
- **Solution:**
  1. Activate the virtual environment:
     ```sh
     cd /var/www/github/GREGor_dashboard/server
     source env/bin/activate
     ```
  2. Check if Gunicorn is installed:
     ```sh
     pip list | grep gunicorn
     ```
  3. If not installed, install it:
     ```sh
     pip install gunicorn
     ```
  4. Ensure the systemd service file uses the correct virtual environment by setting:
     ```ini
     Environment="PATH=/var/www/github/GREGor_dashboard/server/env/bin"
     ```

---

## 2. Unix Socket Issues Between Gunicorn and NginX

### **Socket Creation and Location**
- **Issue:** Gunicorn cannot create the Unix socket because of permission problems in `/var/run/`.
- **Solution:**
  - **Option 1 (Recommended):** Change the socket path to a directory where the service user (e.g., `dashboard`) has write access, for example:
    - Update Gunicorn service file:
      ```ini
      ExecStart=/var/www/github/GREGor_dashboard/server/env/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/github/GREGor_dashboard/server/gregor.sock \
          config.wsgi:application
      ```
    - Update NginX configuration accordingly.
  - **Option 2:** Create a dedicated directory in `/var/run/`:
    ```sh
    sudo mkdir /var/run/gregor
    sudo chown dashboard:developers /var/run/gregor
    sudo chmod 770 /var/run/gregor
    ```
    - Update the service file to bind to `/var/run/gregor/gregor.sock`.

### **Permission Denied When Connecting to the Socket**
- **Cause:** NginX cannot access the Gunicorn socket because of SELinux restrictions or file permission issues.
- **Solution:**
  1. **Fix File Permissions:**  
     Ensure the socket is writable:
     ```sh
     sudo chown nginx:developers /var/run/gregor.sock
     sudo chmod 660 /var/run/gregor.sock
     ```
  2. **Fix SELinux Context:**  
     Set the proper SELinux label:
     ```sh
     sudo semanage fcontext -a -t httpd_var_run_t "/var/run/gregor.sock"
     sudo restorecon -v /var/run/gregor.sock
     ```
  3. **Allow NginX Connections in SELinux:**  
     Create a custom policy module if needed:
     ```sh
     sudo ausearch -m AVC,USER_AVC -c nginx --raw | audit2allow -M nginx_gunicorn
     sudo semodule -i nginx_gunicorn.pp
     ```
     And also enable related booleans:
     ```sh
     sudo setsebool -P httpd_can_network_connect on
     sudo setsebool -P httpd_can_network_relay on
     ```

---

## 3. NginX Configuration Issues

### **502 Bad Gateway Errors**
- **Cause:** NginX cannot connect to the Gunicorn socket due to incorrect socket path or permission issues.
- **Solution:**
  - Verify the `proxy_pass` in your NginX configuration points to the correct socket file. For example:
    ```nginx
    location /api/ {
        proxy_pass http://unix:/var/run/gregor.sock;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    ```
  - Restart NginX:
    ```sh
    sudo nginx -t
    sudo systemctl restart nginx
    ```
  - Check the NginX error logs for further clues:
    ```sh
    sudo tail -f /var/log/nginx/error.log
    ```

---

## 4. Static Files and Database Permission Issues

### **Django `collectstatic` PermissionError**
- **Cause:** The `STATIC_ROOT` is incorrectly defined or the directory is not writable.
- **Solution:**
  1. **Update `settings.py`:**  
     Set `STATIC_ROOT` without a leading slash:
     ```python
     STATIC_ROOT = os.path.join(BASE_DIR, "static")
     ```
  2. **Create and Set Permissions on the Static Directory:**
     ```sh
     sudo mkdir -p /var/www/github/GREGor_dashboard/server/static
     sudo chown -R dashboard:developers /var/www/github/GREGor_dashboard/server/static
     sudo chmod -R 775 /var/www/github/GREGor_dashboard/server/static
     ```
  3. **Run:**
     ```sh
     python manage.py collectstatic
     ```

### **SQLite Database is Read-Only**
- **Cause:** The database file is owned by a different user or lacks write permissions.
- **Solution:**
  - Change ownership and permissions so that the service user (e.g., `dashboard`) can write:
    ```sh
    sudo chown dashboard:developers /var/www/github/GREGor_dashboard/server/db.sqlite3
    sudo chmod 664 /var/www/github/GREGor_dashboard/server/db.sqlite3
    ```
  - Verify that the parent directory is accessible:
    ```sh
    ls -ld /var/www/github/GREGor_dashboard/server/
    ```
    If needed, adjust:
    ```sh
    sudo chown -R dashboard:developers /var/www/github/GREGor_dashboard/server
    sudo chmod -R 775 /var/www/github/GREGor_dashboard/server
    ```

---

## 5. SELinux Snapshot for Future Reference

### **Saving Your SELinux Settings**
```sh
sh /var/www/github/GREGor_dashboard/server/utilities/selinux_snapshot.sh
```

---

## 6. Additional Tips
- **Restart Services After Changes:**
  ```sh
  sudo systemctl restart gregor
  sudo systemctl restart nginx
  ```
- **Check Logs for Debugging:**
  ```sh
  sudo journalctl -u gregor --no-pager | tail -20
  sudo tail -f /var/log/nginx/error.log
  ```

---

## Useful Commands for Checking Status and Debugging

**gunicorn**

Start|Restart|Stop gunicorn - systemctl [start|restart|stop] gunicorn
logging commands...

**nginx**

Start|Restart|Stop nginx - systemctl [start|restart|stop] nginx
logging commands

**system**

Locate where an executable named [PROGRAM] is - which [PROGRAM]
Example:  which python