# Swagger Documentation

For most of the swagger endpoints you need to provide token authentication. The token is a JSON Web Token (JWT)[https://auth0.com/docs/secure/tokens/json-web-tokens] that is created by a log in action. Each log in instance has a unique JWT. A log out will blacklist a JWT in the server DB as well as remove it from the local storage. 

To authenticate withe the Swagger API you need to provide a valid JWT to the page before executing any of the APIs. 

## Obtaining the JWT 
1. Log in to the site. 

![Screenshot 2025-04-16 at 10 11 02 AM](https://github.com/user-attachments/assets/c1e14921-0131-4b3f-badb-b14839ba2841)

2. click on the Profile tab

![Screenshot 2025-04-16 at 10 17 38 AM](https://github.com/user-attachments/assets/de065295-8675-47e7-816f-56223b17ed97)

3. click on "copy access token"

![Screenshot 2025-04-16 at 10 18 18 AM](https://github.com/user-attachments/assets/86c16691-505f-4536-8932-78a12191c83b)

4. navigate to the Swagger page

5. lick on the "Authorize" button at the top of the page

![Screenshot 2025-04-16 at 10 20 46 AM](https://github.com/user-attachments/assets/0a7381f6-4f76-43b6-a755-819548c4af7a)

6. When the pop-up appears type "Bearer " and then past the token

![Screenshot 2025-04-16 at 10 23 10 AM](https://github.com/user-attachments/assets/b78f98f7-7cb7-47ad-82e5-b94e5119eb07)

7. Click the "Authorize" button and then close the pop-up. 

**Caution**: A page refresh will remove the authentication and you will have to enter it again. 

You should see that all of the padlock icons have gone from an "unlocked" state to a "locked" state.

![Screenshot 2025-04-16 at 10 23 54 AM](https://github.com/user-attachments/assets/85c58159-5420-4cbd-b27c-85d993b1669c)
==>
![Screenshot 2025-04-16 at 10 24 17 AM](https://github.com/user-attachments/assets/46aa1c4b-07ba-4ea8-b12b-fdf27cf12343)



## Submitting a request: Authorized
The Swagger site uses the database modles and serializers to render what is expected for a request submission and what the server will return for a given request. *This site is still under development so sonme of the functions may not be perfect. If you notice any inconsistencies please (submit an issie)[https://github.com/UCI-GREGoR/GREGor_dashboard/issues/new*

1. Click the "Try it out" button
2. For most cases once the buttion is pressed there will be a URL paramater to fill out or a POST data set to fill out for submission. Fill out the required fields an then click the submit button. 
3. The Swagger sitew will then render a CURL representation of the request, the request URL, and the response. It will also show the respons code, response body, and the response headers.

	a. respons code: HTML response code returned from the request.
	
	b. response body: Data returned from the request. 
	
	c. response headers: headers submitted with the request. 
