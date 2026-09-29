Using ICTS-Dashboard with Google OAuth

Google OAuth can be used for the following functions
* Local user authentication swagger or reactjs frontend
* Obtaining Google Cloud (gcloud) access and refresh tokens for object uploads to Terra

Prerequisites

* Create a Google Cloud Web Application for OAuth authentication
  * Follow [Google's instructions](https://support.google.com/cloud/answer/15549257?sjid=11949456351444309656-NC#zippy=%2Cweb-applications) using a pre-existing Google account
    * A credit card will be needed to set up a billing account
      * This billing account will be needed for Terra/AnVIL workspace setup later

  * After creating the web application, paste the `CLIENT ID` and `CLIENT SECRET` in the .secrets file

  * Set Authorised JavaScript origins
    * For a demo system running on `LOCALHOST` and the reactjs/django running on ports `3000`/`8000` respectively add the following origins:
      * http://localhost
      * http://localhost:3000
      * http://localhost:8000
      * Change the port numbers accordingly to match your configuration's reactjs and django ports
    * For a system configured with `HTTPS`, provide the domain name as the origin:
      * https://genomics.icts.uci.edu  # for the prod server
      * https://accicts201l.hs.uci.edu  # for the dev server

  * Set Authorised redirect URLs
    * For a demo system running on `LOCALHOST`, use the django port and callback handle
      * http://localhost:8000/api/auth/oauth/callback/
    * For a system running with `HTTPS`, add the callback handle to the domain
      * https://genomics.icts.uci.edu/api/auth/oauth/callback/
      * https://accicts201l.hs.uci.edu/api/auth/oauth/callback/

  * Set up the OAuth consent screen per Google's instructions

* Create a new Terra/AnVIL workspace to upload files
  * Follow [Terra's guide](https://broadinstitute.github.io/viral-workshops/broad-viral-ngs/workspace-setup.html)
    * Make sure the Google account used to sign in with OAuth has permission to write to the AnVIL workspace

Signing in

* Navigate to the oauth helper portal
  * On LOCALHOST instances, this would be at http://localhost:8000/api/auth/oauth/helper/
  * On PROD instances, this would be at https://genomics.icts.uci.edu/api/auth/oauth/helper/
  * On DEV instances, this would be at https://accicts201l.hs.uci.edu/api/auth/oauth/helper/
* Click on `Sign in with Google` at the top to sign in to a local account using OAuth
* Walk through Google's consent screens, then navigate to the Swagger page and verify you are signed in
* Call `/auth/oauth/whoami/` to confirm the correct account is signed in
  * If Google gcloud is set up, the flag `google_connected` should show `TRUE`
* Navigate back to the oauth helper portal and click on `Connect Google for Firecloud`
* Walk through Google's consent screens and redirect to the swagger page
  * `google_connected` should now show `TRUE` if not before

Uploading

* Call `/auth/oauth/upload/` to upload files
  * Copy the `bucket_name` and `google_project_id` from the Terra workspace dashboard
    * Bucket names start with `fc-secure-...` and project IDs start with `terra-...`
