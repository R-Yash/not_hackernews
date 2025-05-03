from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from db import get_db
from models import User, UserCreate, Token, TokenData

router = APIRouter(tags=["Authentication"])

SECRET_KEY = "97701342c97c43116408e06efcd7081c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.

    Args:
        data: The dictionary payload to encode in the token (typically includes 'sub': username).
        expires_delta: Optional timedelta object for token expiry. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        The encoded JWT access token string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> str:
    """
    Dependency to get the current authenticated user from a JWT token.

    Args:
        token: The OAuth2 bearer token extracted from the request header.
        db: The database session dependency.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid, expired, or the user doesn't exist.

    Returns:
        The username of the authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception
    return username

@router.post("/signup", status_code=201)
async def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the database.

    Args:
        user_in: User creation data (username, password).
        db: The database session dependency.

    Raises:
        HTTPException: 400 Bad Request if the username is already registered.

    Returns:
        A confirmation message.
    """
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User(username=user_in.username, hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    return {"msg": "User created successfully"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and returns an access token.

    Args:
        form_data: Form data containing username and password.
        db: The database session dependency.

    Raises:
        HTTPException: 400 Bad Request if authentication fails.

    Returns:
        An access token and token type.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout():
    return {"msg": "Logout successful"}

@router.get("/users", response_model=list[str])
async def get_users(db: Session = Depends(get_db)):
    return [u.username for u in db.query(User).all()]