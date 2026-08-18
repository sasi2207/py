from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError

from database import engine, Base, get_db
import models
import schemas

# ----------------------------------------------------
# 1. Configuration & Security Settings
# ----------------------------------------------------
SECRET_KEY = "your-super-secret-jwt-key-techsasi-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Automatically create tables in MySQL
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TechSasi ERP + CRM API",
    version="1.0.0",
    description="Authentication and ERP backend connected to MySQL"
)

# ----------------------------------------------------
# 2. CORS Middleware
# ----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# 3. Helper Functions
# ----------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ----------------------------------------------------
# 4. Auto-Seed Demo Users on Startup
# ----------------------------------------------------
@app.on_event("startup")
def seed_demo_users():
    db = next(get_db())
    try:
        demo_accounts = [
            ("admin@techsasi.com", "Admin@123", "System Administrator", "admin"),
            ("trainer@techsasi.com", "Trainer@123", "Lead Trainer", "trainer"),
            ("student@techsasi.com", "Student@123", "Enrolled Student", "student"),
        ]
        for email, password, name, role in demo_accounts:
            existing = db.query(models.User).filter(models.User.email == email).first()
            if not existing:
                new_user = models.User(
                    email=email,
                    hashed_password=hash_password(password),
                    full_name=name,
                    role=role
                )
                db.add(new_user)
        db.commit()
    finally:
        db.close()

# ----------------------------------------------------
# 5. Authentication Endpoints
# ----------------------------------------------------
@app.post("/api/auth/login", response_model=schemas.LoginResponse)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    email_clean = credentials.email.lower().strip()
    user = db.query(models.User).filter(models.User.email == email_clean).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_payload = {
        "sub": user.email,
        "id": user.id,
        "role": user.role,
        "name": user.full_name,
    }
    access_token = create_access_token(data=token_payload)

    return schemas.LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserResponse.from_orm(user)
    )

@app.post("/api/auth/register", response_model=schemas.LoginResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    email_clean = user_data.email.lower().strip()
    existing = db.query(models.User).filter(models.User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    new_user = models.User(
        email=email_clean,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role or "student"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.email, "id": new_user.id, "role": new_user.role})

    return schemas.LoginResponse(
        access_token=token,
        token_type="bearer",
        user=schemas.UserResponse.from_orm(new_user)
    )

@app.get("/")
def root():
    return {"message": "TechSasi ERP + CRM API is running. Access interactive docs at /docs"}