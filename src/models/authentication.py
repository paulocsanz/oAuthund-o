class Authentication:
    def __init__(self, username, password, client_id, cookie, id = None, code = None, is_encrypted=False):
        self.id = id
        self.code = code or random_string(app.config["CODE_SIZE"])
        self.username = username
        self.client_id = client_id
        self.cookie = cookie
        self.encrypted_password = password if is_encrypted else encrypt(code, password)
        self.client_id = client_id

    def save(self):
        with DB() as db:
            self.id = db.insert(
                    "INSERT INTO authentications "
                    "(username, encrypted_password, client_id) "
                    "VALUES (%s, %s, %s, %s)",
                    self.username,
                    self.encrypted_password,
                    self.client_id)

    def retrieve_password(username, client_id, code):
        with DB() as db:
            encrypted_password = db.find(
                    "SELECT encrypted_password "
                    "FROM authentications "
                    "WHERE username = %s"
                    "      AND client_id=%s",
                    username,
                    client_id)
        return decrypt(code, encrypted_password) 
