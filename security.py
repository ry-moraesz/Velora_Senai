from datetime import datetime,timedelta,timezone
from jose import jwt,JWTError
from pwdlib import PasswordHash
from app.core.config import settings
hasher=PasswordHash.recommended(); ALGORITHM='HS256'
def hash_password(password:str)->str: return hasher.hash(password)
def verify_password(password:str,hashed:str)->bool: return hasher.verify(password,hashed)
def token_for(user_id:int,company_id:int,role:str): return jwt.encode({'sub':str(user_id),'company':company_id,'role':role,'exp':datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_minutes)},settings.jwt_secret,algorithm=ALGORITHM)
def decode_token(token:str):
 try:return jwt.decode(token,settings.jwt_secret,algorithms=[ALGORITHM])
 except JWTError:return None
