# GREGoR Data Dcitionary to DB

## Step 1: Set Up Google Sheets API
Google Cloud Console Setup:

Go to the [Google Cloud Console](https://console.cloud.google.com/).

Create a new project or select an existing one.

Navigate to "APIs & Services" > "Library" and enable the Google Sheets API for your project.
Create Credentials:

In the "Credentials" section, click on “Create Credentials” and select “Service account”.

Fill out the necessary details for the service account and grant it the appropriate roles (e.g., Editor or Viewer depending on your needs).

Create a key for this service account in JSON format and download it. This file will be used to authenticate your requests.

## Step 2: Install gspread and oauth2client
Install the necessary Python libraries by running:

```
pip install gspread oauth2client
```

## Step 3: Set Up Authentication
Use the downloaded JSON key file to authenticate using gspread:

```
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_your_credentials_file.json', scope)

# Authorize the clientsheet 
client = gspread.authorize(creds)

```

## Step 4: Open the Spreadsheet by URL
Once authorized, you can open a spreadsheet by its URL:

```
# Make sure you share your Google sheet with the email address of your service account

url = 'https://docs.google.com/spreadsheets/d/your_spreadsheet_id'

sheet = client.open_by_url(url)

# Get the first sheet of the Google Sheet
worksheet = sheet.get_worksheet(0)

# Get all records of the data as a list of dictionaries
records = worksheet.get_all_records()
print(records)
```

Notes:
- Sharing: Make sure to share your Google Sheet with the email address of your created service account (you can find this in your Service Account details).
- URL: Replace 'your_spreadsheet_id' with the actual ID from your Google Sheets URL. The ID is typically between "docs.google.com/spreadsheets/d/" and the next "/edit" in the URL.
