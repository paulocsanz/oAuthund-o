# How it works

## What is this

Since this is just a wrapper for SIGA's API (https://portalaluno.ufrj.br) we need to become a interface between the APP and SIGA. To do that we need to store username and passwords. But that's really problematic, we don't have any intention of having access to user's passwords, so we encrypt it.

But to make the actual request we need to decrypt it and store in memory the password, it's an ethical stance that we will never store persistently this password, or the key to decrypt the encrypted password that is indeed stored. This is hardly ideal, but the only solution would be if SIGA itself provided the OAuth api. They don't, not publicly, and I've asked them a bunch of times, being completely ignored in all of those, they just stopped answering my messages. And no, it's not because of the need to implement it, because they do provide that API, which was used by `Caronaê` in the past. Maybe they don't want to maintain it. So lets do it for them.

We will work to make this as legitimate as possible, to make sure this system can be trusted, either by using the name of the [Grêmio de ECI](https://gremio-eci.github.io) or some laboratory whithin UFRJ. It's currently in development stages so we haven't started that process yet.

## How it works

The cryptographed password generated when the user logs-in with a registered app is stored together with the hashed encryption key (the token). That encryption key is sent to the `redirect_uri`, so the client app can store it to make requests authorized as the SIGA's user.

Whenever the client app wants to make a request to SIGA's API it sends it to us, with the authorization `code` (its `client_id` and `client_secret`. That `code` is then hashed and searched for in the database, if it's found, and it's from the requested app the `encrypted_password` stored with it is then decrypted in memory, using the `code` sent from the user. Neither the code, nor the password actually touch the db, they always stay in memory.

With the decrypted password in memory the specific request to SIGA's API is made, the HTML is parsed and data is returned to the client (if they are authorized to do so - authorization has not been implemented yet, since this repository is work in progress).

When the request is done, the password and the token are deleted from the server's memory.

That means the client app holds the encryption key, but it can never access the password. Ideally the token would stay with the user, making sure only they store the to decrypt the password (ideally in a http-only secure and temporary cookie in their browser). But this is not currently possible with OAuth2.

## Future

The ideal future is that SIGA provides that API and allows (at least) UFRJ's students to create apps integrated with their database. We can't ensure this will ever happen, the most we can is provide a solution and maybe even pressure to integrate it.

But we would like to improve the protocol, maybe exploring OpenID authenticate and offering a API that can be used on the client side, keeping everything in cookie, never touching the app's server. We need your help to rethink this protocol to make it safer for the user.

