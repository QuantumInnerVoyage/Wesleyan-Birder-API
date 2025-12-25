# Wesleyan Birder API

*Where Cardinals soar and citizen science takes flight!*

A FastAPI backend for an AI-powered birdwatching app that combines Gemini AI bird identification with the scholarly traditions of Wesleyan University.

## Features

- **AI Bird Identification**: Upload a photo and let Gemini identify the species, with special recognition for birds in the Field Guide to the Birds of Wesleyan
- **Life List Tracking**: Keep your personal bird sightings secure and organized with JWT authentication
- **Citizen Science Ready**: ORCID iD integration for scholarly data export
- **Wesleyan Cardinal Aesthetic**: Because every birder deserves a touch of crimson

## The 16 Species of Wesleyan

Our Field Guide features: Northern Cardinal (the mascot!), American Robin, Blue Jay, House Sparrow, European Starling, American Crow, Mourning Dove, Red-tailed Hawk, American Goldfinch, Black-capped Chickadee, White-breasted Nuthatch, Downy Woodpecker, Carolina Wren, Eastern Bluebird, Song Sparrow, and Dark-eyed Junco.

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

## Running the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database for users and sightings
- **Gemini AI** - Bird image identification
- **JWT** - Secure authentication

*Go Cardinals!*
