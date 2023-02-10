<h1 align="center">OAuth 2.0 service</h1>
      
<p align="center">
  <a href="#about">About</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#wiki">Wiki</a> 
</p>

---

## About

This **OAuth 2.0** service is made to be a generic implementation of the framework, designed to work with client credentials grant. 


## Installation

**[Download](https://github.com/UMinho-Netedge/oauth-server/archive/refs/heads/master.zip)** the latest version here.


## Features

### OAuth-server

#### Uses a MongoDB database to save the information about registered clients and active tokens in the system.
#### Uses JSON Schemma to verify authorization scopes of the clients.

#### Endpoints:

* **/register** -> For a new client to be registered on the Authorization server.
* **/token** -> For the client to request an access token.
* **/validate_token** -> Made to validate an access token.
* **/delete** -> Made to delete a client by request. Also, it deletes all active tokens associated with it.

### OpenID-server

At the moment this implementation is not using a database for storing data, but can be easly done.

#### Endpoints:

* **/login** -> For a client to login at Google, which will answer with the tokens.
* **/validate** -> To validate the id tokens.
* **/refresh** -> To get a new access token using a refresh token.


## Wiki

For more information on OAuth 2.0 framework, visit their website **[here](https://oauth.net/2/)**.
