from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app.database import engine, get_db, Base
from app.models import User, Sighting
from app.schemas import (
    UserCreate, UserResponse, UserUpdate, Token,
    SightingCreate, SightingResponse, BirdIdentificationResponse
)
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user
)
from app.config import settings
from app.bird_identifier import identify_bird

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wesleyan Birder API",
    description="""
# Welcome to the Wesleyan Birder API

*Where Cardinals soar and citizen science takes flight!*

This API powers the Wesleyan Birder app, combining AI-powered bird identification 
with the scholarly traditions of Wesleyan University. Track your Life List, 
contribute to citizen science, and discover the avian wonders of Connecticut.

## Features

- **AI Bird Identification**: Upload a photo and let Gemini identify the species, 
  with special recognition for birds in the Field Guide to the Birds of Wesleyan
- **Life List Tracking**: Keep your personal bird sightings secure and organized
- **Citizen Science Ready**: ORCID iD integration for scholarly data export
- **Wesleyan Cardinal Aesthetic**: Because every birder deserves a touch of crimson

## The 16 Species of Wesleyan

Our Field Guide features: Northern Cardinal (the mascot!), American Robin, Blue Jay, 
House Sparrow, European Starling, American Crow, Mourning Dove, Red-tailed Hawk, 
American Goldfinch, Black-capped Chickadee, White-breasted Nuthatch, Downy Woodpecker, 
Carolina Wren, Eastern Bluebird, Song Sparrow, and Dark-eyed Junco.

*Go Cardinals!*
    """,
    version="1.0.0",
    contact={
        "name": "Wesleyan Birder Team",
    },
    license_info={
        "name": "MIT",
    },
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Wesleyan Birder API",
        "tagline": "Where Cardinals soar and citizen science takes flight!",
        "docs": "/docs",
    }


@app.post("/auth/register", response_model=UserResponse, tags=["Authentication"],
          summary="Register a new birder")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new Wesleyan Birder account.
    
    - **username**: Your birder identity (3-50 characters)
    - **email**: For updates on rare sightings
    - **password**: Keep your Life List secure
    - **orcid_id**: Optional ORCID iD for citizen science contributions
    """
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        orcid_id=user.orcid_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/auth/login", response_model=Token, tags=["Authentication"],
          summary="Login to your birder account")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate and receive a JWT token to access your Life List.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse, tags=["Users"],
         summary="Get your birder profile")
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Retrieve your profile information, including your ORCID iD for citizen science.
    """
    return current_user


@app.put("/users/me", response_model=UserResponse, tags=["Users"],
         summary="Update your birder profile")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update your profile. Add your ORCID iD to prepare for scholarly data export!
    """
    if user_update.email:
        current_user.email = user_update.email
    if user_update.orcid_id is not None:
        current_user.orcid_id = user_update.orcid_id
    
    db.commit()
    db.refresh(current_user)
    return current_user


@app.post("/identify", response_model=BirdIdentificationResponse, tags=["Bird Identification"],
          summary="Identify a bird from an image")
async def identify_bird_endpoint(
    file: UploadFile = File(..., description="Upload a bird photo (JPEG, PNG)"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an image of a bird and let our AI identify it!
    
    The Wesleyan Birder AI will return:
    - **Common name** of the bird
    - **Scientific name** in Genus species format
    - **Wesleyan Fact** connecting the bird to Wesleyan University or Connecticut
    - Whether it's one of the **16 species in the Field Guide to the Birds of Wesleyan**
    
    *Pro tip: The Northern Cardinal is our mascot - spot one for extra Wesleyan pride!*
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload an image file"
        )
    
    image_data = await file.read()
    result = await identify_bird(image_data)
    
    return BirdIdentificationResponse(**result)


@app.post("/sightings", response_model=SightingResponse, tags=["Sightings"],
          summary="Record a new bird sighting")
async def create_sighting(
    sighting: SightingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new bird to your Life List!
    
    Record your sighting with:
    - **bird_name**: Common name of the bird
    - **scientific_name**: Optional scientific name
    - **latitude/longitude**: Where you spotted it
    - **mansion_notes**: Your personal observations
    - **wesleyan_fact**: Any Wesleyan connection you discovered
    """
    db_sighting = Sighting(
        bird_name=sighting.bird_name,
        scientific_name=sighting.scientific_name,
        latitude=sighting.latitude,
        longitude=sighting.longitude,
        mansion_notes=sighting.mansion_notes,
        wesleyan_fact=sighting.wesleyan_fact,
        user_id=current_user.id,
    )
    db.add(db_sighting)
    db.commit()
    db.refresh(db_sighting)
    return db_sighting


@app.get("/sightings", response_model=List[SightingResponse], tags=["Sightings"],
         summary="Get your Life List")
async def get_sightings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve your personal Life List of bird sightings.
    
    Your Life List is private and only accessible with your authentication token.
    """
    sightings = db.query(Sighting).filter(
        Sighting.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return sightings


@app.get("/sightings/{sighting_id}", response_model=SightingResponse, tags=["Sightings"],
         summary="Get a specific sighting")
async def get_sighting(
    sighting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve details of a specific bird sighting from your Life List.
    """
    sighting = db.query(Sighting).filter(
        Sighting.id == sighting_id,
        Sighting.user_id == current_user.id
    ).first()
    
    if not sighting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sighting not found in your Life List"
        )
    return sighting


@app.delete("/sightings/{sighting_id}", tags=["Sightings"],
            summary="Delete a sighting")
async def delete_sighting(
    sighting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a sighting from your Life List (we won't tell anyone you miscounted!).
    """
    sighting = db.query(Sighting).filter(
        Sighting.id == sighting_id,
        Sighting.user_id == current_user.id
    ).first()
    
    if not sighting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sighting not found in your Life List"
        )
    
    db.delete(sighting)
    db.commit()
    return {"message": "Sighting removed from your Life List"}
