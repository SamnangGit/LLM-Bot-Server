import uuid

class SessionUtils:
    @staticmethod
    def generate_session_id():
        return str(uuid.uuid4())
    

    @staticmethod
    def get_session_id(request):
        return request.cookies.get("uuid")