# MGRC GREGoR Dashboard Local Deployment Instructions & Notes

## System Setup
### Requirements
- [Node.js](https://nodejs.org/en)
- [Python 3](https://www.python.org/downloads/)
- [PyEnv](https://github.com/pyenv/pyenv) (optional but recommended)

## Clone the repo

- For HTTPS access: 

		git clone https://github.com/UCI-GREGoR/GREGor_dashboard/

- For SSH access*(RECCOMENDED)*: 

		git@github.com:UCI-GREGoR/GREGor_dashboard.git

**Then**

	cd GREGor_dashboard/

**If you need to use a branch other than `main`:**

`git switch <BRANCH NAME>` *(for whatever branch you need)*

## MGRC GREGoR Dashboard Server deployment  (GREGor_dashboard/server)

**Open a new terminal and retrun to the project root**

	cd PATH/TO/PROJECT/GREGor_dashboard

### Enter the server directory, create a virtual environment, and install the required packages

##### For Mac/Linux: *[pyenv(optional)](https://github.com/pyenv/pyenv?tab=readme-ov-file#simple-python-version-management-pyenv)*

	cd server
	pyenv local 3.11.1 
	python3 -m venv env
	source env/bin/activate
	pip3.9 install -r requirements.txt

##### For Windows:

	cd server
	python -m venv env
	source env/Scripts/activate
	pip install -r requirements.txt


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
[SERVER]
DEBUG=True
ALLOWED_HOSTS=*
SERVER_VERSION=MAJOR.MINOR.PATCH
DASHBOARD_URL=http://localhost:3000
DATABASE=db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

#### Set up DB
---
##### Option #1: Use existing DB

	cp admin/db.sqlite3 .
	python3 manage.py migrate

````
superusername: wheel
password: wheel
````

---
##### Option #2: Create a new DB with fixture data
Create a DB:

	python3 manage.py migrate

Load the DB with test data:

	python manage.py loaddata config/fixtures/local_data.json

---
#### Run Server
`python3 manage.py runserver`

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

## MGRC GREGoR Dashboard Client deployment  (GREGor_dashboard/client)

### Enter the repository, create a environment file, and install the required packages

	cd GREGor_dashboard/client/

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
