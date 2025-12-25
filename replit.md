# Wesleyan Birder API

## Overview
A FastAPI backend for an AI-powered birdwatching app that combines Gemini AI bird identification with citizen science features.

## Project Structure
```
app/
├── __init__.py
├── main.py          # FastAPI application with all endpoints
├── config.py        # Configuration and settings
├── database.py      # PostgreSQL database connection
├── models.py        # SQLAlchemy models (User, Sighting)
├── schemas.py       # Pydantic schemas for request/response
├── auth.py          # JWT authentication utilities
└── bird_identifier.py # Gemini AI bird identification
```

## Key Features
- **AI Bird Identification**: `/identify` endpoint uses Gemini AI to analyze bird images
- **PostgreSQL Database**: Stores users and sightings with full CRUD operations
- **JWT Authentication**: Secure access to Life List features
- **ORCID iD Support**: User profiles include ORCID iD for citizen science data export
- **Wesleyan Cardinal Aesthetic**: API docs reflect the university's bird mascot theme

## API Endpoints
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Get JWT access token
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update profile (including ORCID iD)
- `POST /identify` - Upload image for AI bird identification
- `POST /sightings` - Record a new bird sighting
- `GET /sightings` - Get user's Life List
- `GET /sightings/{id}` - Get specific sighting
- `DELETE /sightings/{id}` - Remove sighting

## Database Models
- **User**: id, username, email, hashed_password, orcid_id, created_at
- **Sighting**: id, bird_name, scientific_name, timestamp, latitude, longitude, mansion_notes, wesleyan_fact, user_id

## Running the Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

## Recent Changes
- December 25, 2025: Initial project setup with full API implementation
