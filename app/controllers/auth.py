from sqlalchemy.orm import Session
from database.Identity import Identity
from datetime import date
from database.db_connector import DBConnector
from passlib.hash import pbkdf2_sha256
from datetime import datetime
import jwt
from dotenv import load_dotenv
import os

load_dotenv()

def register_identity(data, session: Session):
    username = data['username']
    email = data['email']
    password = data['password']
    hashed_password = pbkdf2_sha256.hash(password)
    status = True
    created_at = datetime.now()
    updated_at = datetime.now()

    identity = Identity(
            username=username,
            email=email,
            password=hashed_password,
            status=status,
            created_at=created_at,
            updated_at=updated_at
        )
    session.add(identity);
    session.commit();


def login_identity(data, session: Session):
    email = data['email']
    password = data['password']
    hashed_password = pbkdf2_sha256.hash(password)
    user = session.query(Identity).filter(Identity.email == email).first()
    if not user:
        return "invalid email"
    if not pbkdf2_sha256.verify(password, user.password):
        return "invalid password"
    return {"message": "Login successful", "token": create_access_token(user)}
        

def create_access_token(identity: Identity):
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    data = {
        'username': identity.username,
        'email': identity.email
    }
    identity_token = jwt.encode(data, SECRET_KEY, algorithm="HS256")
    return identity_token