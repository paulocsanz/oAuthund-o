from ..models import Application

def get_apps(user_id):
    return Application.find_by_user(user_id)

def get_client(client_id):
    return Application.find_by_client(client_id)

def register_app(username, name, description, redirect_uri):
    app = Application(username, name, description, redirect_uri)
    app.save()
    return app.client_id

def delete_app(username, client_id):
    Application.delete(username, client_id)
