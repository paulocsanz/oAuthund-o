# Sigalogado

oAuth2 API for SIGA's (UFRJ) database

## Dependencies

- python3
- mysql

For ubuntu users run:

```
sudo apt install mysql-server libmysqlclient-dev
```

## Installing

Create a MySQL account for this server to use

Linux:

Don't forget to change the password in `{YOUR-PASSWORD-HERE}`

```
sudo mysql
CREATE USER 'sigalogado'@'localhost' IDENTIFIED BY '{YOUR-PASSWORD-HERE}';
GRANT ALL PRIVILEGES ON *.* TO 'sigalogado'@'localhost';
```

This is not the best sysadmin move, be careful with all those permissions. TODO: improve this.

Run:

`python3 install.py`

If it fails while installing flask-mysqldb because of `mysql_config` the mysql client library is probably missing on your system (libmysqlclient-dev on Ubuntu).

## Running

To run it locally on linux execute:

`./rundev.sh`

On windows execute:

`./Rundev.ps1`

## What is this and why does it exist

This is a resource server for SIGA, allowing apps to implement login through SIGA, like with facebook, or google, or github. This creates a bunch of possibilities, integrating SIGA with custom apps allows that we, as students, create services to improve our lives. As students of Computer and Information Engineering we create apps like that all the time, but a bunch of times we create a mock server to act as SIGA, because the API is just not there. So nothing we try to do improve our lives as UFRJ's students actually changes anything, it can't be run in production.

Tired of being ignored by SIGA we decided to make our own. Not because they didn't want to implement that API, because it's there and has been used in the past, for example [Caronaê](https://caronae.org/), a app to offer rides to university, is integrated with SIGA. Maybe the maintenance burden of allowing custom apps to integrate with it was not worth it for them. But it is for us.

This is a wrapper for SIGA's HTML API (https://portalaluno.ufrj.br) we need to be a interface between the client app and SIGA. To do that we need to store usernames and passwords. But that's really problematic, we don't have any intention of accessing the user's passwords, so we encrypt them.

But to make the actual request to SIGA we need to decrypt the password and keep it in memory, it's an ethical stance that we will never store persistently this password, or the key to decrypt the encrypted version, that is indeed stored in our database. This is hardly ideal, but the only solution would be if SIGA itself provided the OAuth api, which they refuse to do.

We will work to make this as legitimate as possible, to make sure this system can be trusted, either by using the name of the [Grêmio de ECI](https://gremio-eci.github.io) or some laboratory whithin UFRJ. It's currently in development stages so we haven't started that process yet.

## How it works

An app is registered (only by SIGA's users). That app provides a `redirect_uri` to receive the authentication tokens through and receives a `client_id`. That `client_id` can be public although not ideal, but the `client_secret` should be kept outside of public ey
The cryptographed password generated when the user logs-in with a registered app is stored together with the hashed encryption key (the token). That encryption key is sent to the `redirect_uri`, so the client app can store it to make requests authorized as the SIGA's user.

Whenever the client app wants to make a request to SIGA's API it sends it to us, with the authorization `code` (its `client_id` and `client_secret`. That `code` is then hashed and searched for in the database, if it's found, and it's from the requested app the `encrypted_password` stored with it is then decrypted in memory, using the `code` sent from the user. Neither the code, nor the password actually touch the db, they always stay in memory.

With the decrypted password in memory the specific request to SIGA's API is made, the HTML is parsed and data is returned to the client (if they are authorized to do so - authorization has not been implemented yet, since this repository is work in progress).

When the request is done, the password and the token are deleted from the server's memory.

That means the client app holds the encryption key, but it can never access the password. Ideally the token would stay with the user, making sure only they store the to decrypt the password (ideally in a http-only secure and temporary cookie in their browser). But this is not currently possible with OAuth2.

## Future

The ideal future is that SIGA provides that API and allows (at least) UFRJ's students to create apps integrated with their database. We can't ensure this will ever happen, the most we can is provide a solution and maybe even pressure to integrate it.

But we would like to improve the protocol, maybe exploring OpenID authenticate and offering a API that can be used on the client side, keeping everything in cookie, never touching the app's server. We need your help to rethink this protocol to make it safer for the user.

