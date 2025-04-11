# Swagger Documentation

For most of the swagger endpoints you need to provide token authentication. The token is a JSON Web Token (JWT)[https://auth0.com/docs/secure/tokens/json-web-tokens] that is created by a log in action. Each log in instance has a unique JWT. A log out will blacklist a JWT in the server DB as well as remove it from the local storage. 

To authenticate withe the Swagger API you need to provide a valid JWT to the page before executing any of the APIs. 

## Obtaining the JWT 
1. Log in to the site. 
2. click on the Profile tab
3. click on "copy access token"
4. navigate to the Swagger page
5. lick on the "Authorize" button at the top of the page
6. When the pop-up appears type "Bearer " and then past the token
7. Click the "Authorize" button and then close the pop-up. 

**Caution**: A page refresh will remove the authentication and you will have to enter it again. 

You should see that all of the padlock icons have gone from an "unlocked" state to a "locked" state.


## Submitting a request: Authorized
The Swagger site uses the database modles and serializers to render what is expected for a request submission and what the server will return for a given request. *This site is still under development so sonme of the functions may not be perfect. If you notice any inconsistencies please (submit an issie)[https://github.com/UCI-GREGoR/GREGor_dashboard/issues/new*

1. Click the "Try it out" button
2. For most cases once the buttion is pressed there will be a URL paramater to fill out or a POST data set to fill out for submission. Fill out the required fields an then click the submit button. 
3. The Swagger sitew will then render a CURL representation of the request, the request URL, and the response. It will also show the respons code, response body, and the response headers.

	a. respons code: HTML response code returned from the request.
	
	b. response body: Data returned from the request. 
	
	c. response headers: headers submitted with the request. 