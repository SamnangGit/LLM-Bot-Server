import uuid

class SessionUtils:
    @staticmethod
    def generate_session_id():
        return str(uuid.uuid4())