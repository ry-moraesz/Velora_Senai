from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import decode_token
from app.models import User
bearer=OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')
def current_user(token:str=Depends(bearer),db:Session=Depends(get_db)):
 data=decode_token(token)
 if not data: raise HTTPException(401,'Sessão inválida ou expirada')
 user=db.get(User,int(data['sub']))
 if not user or not user.active or user.company_id!=int(data['company']): raise HTTPException(401,'Usuário indisponível')
 return user
def roles(*allowed):
 def check(user:User=Depends(current_user)):
  if user.role not in allowed: raise HTTPException(403,'Permissão insuficiente')
  return user
 return check
