<h1 align="center">OAuth 2.0 service</h1>
      
<p align="center">
  <a href="#about">About</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#wiki">Wiki</a> 
</p>

---

## About

This repository hosts the implementation of two **OAuth 2.0** services. One is built to function with the client credentials grant, while the other is configured for OpenID. The OpenID version communicates with the ETSI OSM MANO (hereafter referred to as OSM) to verify the authenticity of the login process.


## Installation

Before you proceed, make sure you have Python3 and Docker installed on your system. Although MongoDB isn't a requirement — since we're using a Docker container — it is recommended.

Use pip to install all other necessary modules. We recommend using the Docker Compose files available for each implementation as they have been thoroughly tested and verified to work as intended.

[Download](https://github.com/UMinho-Netedge/oauth-server/archive/refs/heads/master.zip) the latest version here.

## Features

### OAuth-server

The OAuth-server utilizes a MongoDB database to store registered client information and manage active tokens in the system. It also uses JSON Schema to verify the authorization scopes of the clients.

#### Endpoints:

* **/register**: Registers a new client on the Authorization server.
* **/token**: Requests an access token for the client.
* **/validate**: Validates an access token.
* **/delete**: Deletes a client and all its associated active tokens upon request.
* **/clients**: Designed for testing purposes only; returns all clients registered on the server. It should be deactivated for any production implementation.

### OpenID-server

The OpenID-server, similar to OAuth-server, uses a MongoDB database to manage client information and active tokens. It verifies the client's credentials by communicating with the OSM server via the OSM client. After successful login validation, it generates tokens and proceeds similarly to the OAuth-server. However, a key difference is the OpenID-server's provision for refresh tokens, preventing the user from needing to log in every time a token expires.

#### Endpoints:

* **/login**: Validates the login credentials and returns tokens.
* **/validate**: Validates the access tokens.
* **/refresh**: Obtains a new access token using a refresh token.
* **/logout**: Eliminates the currently valid tokens of the user from the database.


## Wiki

For a deeper understanding of the OAuth 2.0 framework, visit the official [OAuth website](https://oauth.net/2/). For information about OpenID, check [here](https://openid.net/).
