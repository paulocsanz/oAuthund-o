from ..models import Authorization

def get_authorizations(username):
    return Authorization.find_all(username)

def get_authorization(client_id, username):
    return Authorization.find(client_id, username)

def set_authorization(client_id, username):
    a = Authorization(client_id, username)
    a.save()
    return a

def delete_authorization(username, client_id):
    Authorization.delete(username, client_id)
