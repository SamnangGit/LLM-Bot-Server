from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from controllers.auth import register_identity, login_identity
from database.db_connector import DBConnector
from sqlalchemy.orm import Session


router = APIRouter()

@router.post('/signup')
async def create_identity(request: Request):
    data = await request.json()
    engine= DBConnector.init_engine()
    session = Session(engine)
    register_identity(data, session)
    return "success"
        
@router.post('/login')
async def login_identity_route(request: Request):
    data = await request.json()
    engine = DBConnector.init_engine()
    session = Session(engine)
    try:
        result = login_identity(data, session)
        return JSONResponse(content=result, status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
        
    