from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from data.database_config import get_db
from data.models import User
from app.core.auth import (
    authenticate_user, 
    create_user, 
    create_access_token, 
    get_current_active_user,
    get_user_by_email,
    get_user_by_username
)
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Pydantic models for API requests
class UserLogin(BaseModel):
    email: str
    password: str

class UserSignup(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# HTML Routes
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page."""
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Display signup page."""
    return templates.TemplateResponse("auth/signup.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login form submission."""
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html", 
            {
                "request": request, 
                "error": "Invalid email or password"
            }
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Redirect to home page with token in cookie
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True,
        max_age=60 * 60 * 24 * 7,  # 7 days
        samesite="lax"
    )
    return response

@router.post("/signup", response_class=HTMLResponse)
async def signup_form(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_db)
):
    """Handle signup form submission."""
    try:
        # Check if user already exists
        if get_user_by_email(db, email):
            return templates.TemplateResponse(
                "auth/signup.html", 
                {
                    "request": request, 
                    "error": "Email already registered"
                }
            )
        
        if get_user_by_username(db, username):
            return templates.TemplateResponse(
                "auth/signup.html", 
                {
                    "request": request, 
                    "error": "Username already taken"
                }
            )
        
        # Create user
        user = create_user(db, email, username, password, full_name)
        
        # Auto-login after signup
        access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key="access_token", 
            value=f"Bearer {access_token}", 
            httponly=True,
            max_age=60 * 60 * 24 * 7,  # 7 days
            samesite="lax"
        )
        return response
        
    except IntegrityError:
        return templates.TemplateResponse(
            "auth/signup.html", 
            {
                "request": request, 
                "error": "User already exists"
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "auth/signup.html", 
            {
                "request": request, 
                "error": "Registration failed. Please try again."
            }
        )

@router.post("/logout")
async def logout():
    """Handle logout."""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

# API Routes
@router.post("/api/login", response_model=Token)
async def login_api(user_data: UserLogin, db: Session = Depends(get_db)):
    """API endpoint for login."""
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }

@router.post("/api/signup", response_model=Token)
async def signup_api(user_data: UserSignup, db: Session = Depends(get_db)):
    """API endpoint for signup."""
    try:
        # Check if user already exists
        if get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        user = create_user(
            db, 
            user_data.email, 
            user_data.username, 
            user_data.password, 
            user_data.full_name
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }
        
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

@router.get("/api/me")
async def get_current_user_api(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user.to_dict() 