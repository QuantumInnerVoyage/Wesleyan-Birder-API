from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Cardinal-worthy username")
    email: EmailStr = Field(..., description="Email address for the birder")
    password: str = Field(..., min_length=6, description="Password to protect your Life List")
    orcid_id: Optional[str] = Field(None, description="ORCID iD for scholarly data export (e.g., 0000-0002-1825-0097)")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    orcid_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    orcid_id: Optional[str] = Field(None, description="ORCID iD for citizen science collaboration")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class SightingCreate(BaseModel):
    bird_name: str = Field(..., description="Common name of the bird spotted")
    scientific_name: Optional[str] = Field(None, description="Scientific name (Genus species)")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude of sighting location")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude of sighting location")
    mansion_notes: Optional[str] = Field(None, description="Your personal observations and notes")
    wesleyan_fact: Optional[str] = Field(None, description="Wesleyan-specific fact about this bird")


class SightingResponse(BaseModel):
    id: int
    bird_name: str
    scientific_name: Optional[str]
    timestamp: datetime
    latitude: Optional[float]
    longitude: Optional[float]
    mansion_notes: Optional[str]
    wesleyan_fact: Optional[str]
    user_id: int

    class Config:
        from_attributes = True


class BirdIdentificationResponse(BaseModel):
    common_name: str = Field(..., description="The bird's common name")
    scientific_name: str = Field(..., description="Scientific name in Genus species format")
    wesleyan_fact: str = Field(..., description="A Wesleyan-specific fact about this bird")
    confidence: str = Field(..., description="Confidence level of the identification")
    in_wesleyan_field_guide: bool = Field(..., description="Whether this is one of the 16 species in the Field Guide to the Birds of Wesleyan")
