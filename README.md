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

#### Uses a MongoDB database to save the information about registered clients and active tokens in the system.

#### Endpoint:

* **/register** -> For a new client to be registered on the Authorization server.
* **/token** -> For the client to request an access token.
* **/validate_token** -> Made to validate an access token.
* **/delete** -> Made to delete a client by request. Also, it deletes all active tokens associated with it.

## Wiki

For more information on OAuth 2.0 framework, visit their website **[here](https://oauth.net/2/)**.
