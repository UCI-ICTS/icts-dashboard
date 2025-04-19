# Welcome to the UCI ICTS Dashboard User Guide

**Table of contents:**
- [Getting an Account](#account)
- [Loggin In & Login Page](#log-in)
- [GREGoR Tables](#gregor-tables)
- [Participant Detail](#participant-detail)
- [Profile](#profile)

<!-- headings -->
<a id="account"></a>
## Getting an Account & Account Activation
1. Contact the site administrator to have them create an account for you.
2. Once your account is created, you will receive an email that looks like this:

<img 
  width="600"
  alt="Screenshot of account activation email"
  src="https://github.com/user-attachments/assets/739c5365-6014-4a6b-9678-68c31fab6d5f"
/>

3. Clicking on the button or pasting the link will take you to the password create page. Once you enter and confirm your password you will be redirected tot the log in page.

<img 
  width="600"
  alt="Screenshot of password create page"
  src="https://github.com/user-attachments/assets/0604be6e-095d-4785-a6d8-fba7a4da9cb9"
/>


<a id="log-in"></a>
## Logging In & Login Page
<img 
  height="500"
  width="530"
  alt="Screenshot of log in page"
  src="https://github.com/user-attachments/assets/24930d83-b737-49b0-bbaf-9b95ec0dfa9d"
/>

Above is a diagram of the log in page and the portions that a user can interact with.
1. **Username**: The user name is created by taking the part of the users email address before the `@` symbol. So the user with the email `jdoe@testing.com` will have `jdoe` as their username
2. **Password**: This is where the user enters their passowrd, once a user has activated their account on the create password page.
3. **Remember Me**: This check box will save the user's authentication credentials to the browser. If this box is **NOT** clicked then the user will have to re-authenticate upon a page refresh. Authentication is managed using JSON Web Tokens ([JWT](https://datatracker.ietf.org/doc/html/rfc7519)).
4. **Log in Button**: Will submit authentication credentials for validation.
5. **Forgot Password**: This will prompt the user to enter their email, and if an account with that email exists they will receive an email prompting them to reset their password (pictured below).

<img 
  width="600"
  alt="Screenshot of password reset email page"
  src="https://github.com/user-attachments/assets/cb73f981-fe1c-4b09-8598-6a4c3a163658"
/>

<a id="gregor-tables"></a>
## GREGoR Tables

### Participants Table

<img
  width="600"
  alt="Screenshot of Participants table"
  src="https://github.com/user-attachments/assets/8a8b11dd-6428-4c91-94fc-2fe6e7ced10b"
/>
#### New Participant Entry
To populate the table, use the **Fetch/Refresh data** button. 
To enter new participants, click on the **+ Add Row** button.
  Participant information can come from services such as RedCAP. 

<img
  width="600"
  alt="Add New participants window"
  src="https://github.com/user-attachments/assets/0bcb3ec6-6287-4080-aedb-4f3d799b24a6"
/>

Toggle the **Edit Mode** to begin entering fields. 
Fields with a * are mandatory while fields with a **ⓘ** can provide information on what each field is for.
Do not navigate away while entering details or your entries may be lost. 
To save your changes, scroll to the bottom and click **Submit**.

#### Collecting cohorts

Cohorts can be collected using the search bar and the **Enable Regex** toggle to the left.
The search bar applies to all fields in the selected table. To search only specific columns, use the **ᗊ Advanced Filters**

Some examples for common queries that can use regex pattern matching include:
- `^PMGRC-.*-0$` to find all probands. The search applies to all fields in the participant table.
  - The syntax is as follows:
    - `^PMGRC-` denotes the field must begin with `PMGRC-`
    - `.*` is a wildcard and represents 0 or many unknown characters.
      - Alternatively, `.+` may be used to represent 1 or many unknown characters.
    - `-0$` denotes the field must end with `-0`
- `^PMGRC-.*-500-.?$` to find all family members of family `500`.
  - Alternatively families can be filtered by the **Advanced Filters** tab.
- `(?=.*CMA)|(?=.*WES)` to find all participants with prior testing with `CMA` or `WES`.
- `(?=.*CMA)(?=.*WES)` to find all participants with prior testing with both `CMA` and `WES`. 
- These queries can often be shortened to remove redundant filters based on known constant values, like the `PMGRC` prefix. 

Alternatively, the **Participants** table can be downloaded as a tab-separated value (TSV) table with the **📥 Download** button. The TSV table can then be processed with your preferred spreadsheet editor (MS Excel, LibreOffice Calc, Google Sheets, etc.)
- Do not export the tables as comma-separated value (CSV) tables as free-text fields such as prior_testing often have commas present which will interfere with column parsing.

<a id="participant-detail"></a>
## Participant Detail
Details of using the participant detail page

<a id="profile"></a>
## Profile
User Profile

<a id="item-three"></a>
### Second Item
Second item content goes here

