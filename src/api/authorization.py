def get_authorization(client_id, username):
    return Authorization.find(client_id, username)
