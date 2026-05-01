# MGRC ICTS Dashboard Local Deployment Instructions & Notes

## System Setup
### Requirements
- [Node.js](https://nodejs.org/en)
- [Python 3](https://www.python.org/downloads/) (only install separately if using Windows)
- [PyEnv](https://github.com/pyenv/pyenv) (optional but recommended)
- [PostgreSQL](https://www.postgresql.org/)

## Clone the repo

- For HTTPS access:

		git clone https://github.com/UCI-ICTS/icts-dashboard/

- For SSH access*(RECCOMENDED)*:

		git@github.com:UCI-ICTS/icts-dashboard.git

**Then**

	cd icts-dashboard/

**If you need to use a branch other than `main`:**

`git switch <BRANCH NAME>` *(for whatever branch you need)*

## MGRC ICTS Dashboard Server deployment  (icts-dashboard/server)

**Open a new terminal and retrun to the project root**

	cd PATH/TO/PROJECT/icts-dashboard

### Enter the server directory, create a virtual environment, and install the required packages

##### For Mac/Linux: *[pyenv(optional)](https://github.com/pyenv/pyenv?tab=readme-ov-file#simple-python-version-management-pyenv)*

	cd server
	pyenv install 3.11
	pyenv local 3.11.13
	python -m venv env
	source env/bin/activate
	pip install -r requirements.txt

##### For Windows:

	cd server
	python -m venv env
	source env/Scripts/activate
	pip install -r requirements.txt

##### Configure PostgreSQL (Linux)

	sudo -u postgres psql  # Open the psql shell

	ALTER USER postgres WITH PASSWORD 'a_new_and_secure_password';  # password is not initially set for the postgres user
	CREATE DATABASE 'ictsdashboard_app';
	ALTER DATABASE ictsdashboard_app OWNER TO postgres;

	\q  # exit the psql shell

	# Open port 5432 on your local postgresql instance's firewall, if the firewall is enabled.

#### Generate the secrets file
----

- Copy the `.secrets.example` to `.secrets`

		cp .secrets.example .secrets

- On linux (or MAC) generate a 32-bytes long PSK key using the openssl command for the `DJANO_KEY`:

		openssl rand -base64 32

- On Windows, generate a 32-bytes long PSK key using the PowerShell command for the `DJANGO_KEY`:

		[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }) -as [byte[]])


- Update the `.secrets` file with the required keys:

```
[DJANGO_KEYS]
SECRET_KEY=

[SERVER]
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SERVER_VERSION=BETA
DASHBOARD_URL=http://localhost:3000
SCHEMA_VERSION=v1.9

[DATABASE]
ENGINE=django.db.backends.postgresql
NAME=ictsdashboard_app
USER=postgres
PASSWORD=postgres
HOST=localhost
PORT=5432

[EMAIL]
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp5000.hs.uci.edu
EMAIL_PORT=25
EMAIL_USE_TLS=False
EMAIL_USE_SSL=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=devnoreply@genomics.icts.uci.edu
```

#### Set up DB
---
##### Option #1: Use existing DB

	python3 manage.py loaddata dump.json

````
superusername: wheel
password: wheel
````

---
##### Option #2: Create a new DB with fixture data
Create a DB:

	python -m manage makemigrations
	python -m manage migrate

Load the DB with test data:

	python -m manage loaddata config/fixtures/intial.json

---
#### Run Server
`python -m manage runserver`

Make sure API is accessible via web browser.

If it worked you should be able to see the API Documentation site at:

`http://localhost:8000/swagger/`

and the Admin site at:

`http://localhost:8000/admin/`

Use the following credentials to log in:

````
username: wheel
password: wheel
````

## MGRC ICTS Dashboard Client deployment  (icts-dashboard/client)

### Enter the repository, create a environment file, and install the required packages

	cd icts-dashboard/client/

**Install Node packages via Node Package Manager (NPM)**

	npm install

### Update the `.env` file with the required keys:
	cp .env.example .env

The APIDB should be `localhost:8000` for local dev.
```
REACT_APP_APIDB="http://localhost:8000"
```

### **Start service**

`npm run start`

This will open `http://localhost:3000/` in your default webbrowser if everything went according to plan. If not, see the [troubleshooting tips](troubleshooting.md).

This terminal will be serving the React frontend.
