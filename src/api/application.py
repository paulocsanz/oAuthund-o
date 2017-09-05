from ..models import Application

def get_client(client_id):
    return Application.find(client_id)

def register_app(name, description, redirect_uri):
    app = Application(name, description, redirect_uri)
    app.save()
    return app.client_id
