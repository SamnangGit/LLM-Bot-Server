from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
# from schemas import identity
# from controllers import auth
# from database.db_connector import get_db
from controllers.auth import register_identity, login_identity
from database.db_connector import DBConnector
from sqlalchemy.orm import Session


router = APIRouter()


@router.post('/register')
async def create_identity(request: Request):
    data = await request.json()
    engine= DBConnector.init_engine()
    session = Session(engine)
    register_identity(data, session)
    return "success"
        

@router.post('/login')
async def login_idenity(request: Request):
    data = await request.json()
    engine= DBConnector.init_engine()
    session = Session(engine)
    return login_identity(data, session)
    # return "success"
        
    