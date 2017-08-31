from ..models import Application

def get_client(client_id):
    return Application.find(client_id)
