
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str):
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str):
    return password_context.verify(password, hashed_pass)


ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 10 minutes
ALGORITHM = "HS256"
JWT_SECRET_KEY = 'dac1b56e1ebc1271469c221644ec83ccdff0de6795b8c9e7529051d8d610c45f'   # should be kept secret
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
JWT_REFRESH_SECRET_KEY = 'cdfaw4afd49jsd0h'    # should be kept secret

def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None :
        user_id = expires_delta
        expires_delta_data = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expires_delta_timestamp = expires_delta_data.timestamp()
        to_encode = {"user_id": user_id, "exp": expires_delta_timestamp, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
        return encoded_jwt
    
def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        user_id = expires_delta
        expires_delta_data = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        expires_delta_timestamp = expires_delta_data.timestamp()
        to_encode = {"user_id": user_id,"exp": expires_delta_timestamp,"sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
        return encoded_jwt

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token,
                              key=JWT_SECRET_KEY,
                              algorithms=["HS256"])
        return dict(status=200, message=payload)
    except Exception as err:
        return dict(status=401, message=str(err))
