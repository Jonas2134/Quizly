# Quizly - A Quiz Application

![Quizly Logo](static/logo.png)

This is the backend code for Quizly, a quiz application that allows users to create Quizzes with AI-generated questions and answers. The application is built using Django and Django REST Framework.

---

## Features

- **User Authentication**: Registration, Login and Logout functionalities with JWT token-based authentication.
- **Quiz Management**: Create, Read, Update, and Delete quizzes.
- **AI Integration**: Generate quiz questions and answers using yt_dlp for audio downloading, Whisper for transcription and Google GenAI for question generation.
- **RESTful API**: Expose endpoints for all functionalities using Django REST Framework.

---

## Tech-Stack

- **Backend**: Django, Django REST Framework
- **Database**: SQLite (default, can be changed to PostgreSQL or others)
- **AI Services**: Whisper, Google GenAI
- **Authentication**: JWT (JSON Web Tokens)
- **Audio Downloading**: yt_dlp
- **Audio Conversion**: ffmpeg

---

## Installation

1. Clone the repository

   ```bash
   git clone https://github.com/Jonas2134/Quizly.git
   cd Quizly
   ```

2. Create a virtual environment

   ```bash
    # Linux/macOS
    python3 -m venv env
    source env/bin/activate
    # Windows
    python -m venv env
    env\Scripts\activate
   ```

3. Install the requirements

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   Create them with:

   ```bash
   cp .env.example .env
   ```

   and edit the `.env` file to configure your environment variables.
   This are the required environment variables:

   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CSRF_TRUSTED_ORIGINS=http://localhost:4200,http://127.0.0.1:4200
   CORS_ALLOW_ALL_ORIGINS=False
   CORS_ALLOW_CREDENTIALS=True
   CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
   ```

5. Apply migrations, create a superuser, and start the server

   ```bash
   # Run migrations
   python manage.py migrate
   # Create a superuser
   python manage.py createsuperuser
   # Start the development server
   python manage.py runserver
   ```

---

## Start pytest

You want to start a pytest? Just run the following command! Please make sure you have pytest installed.

\_When you run the project locally:\_

```bash
pytest
```

---

## API Endpoints

### Authentication

| Endpoint              | Method | Description                            |
| --------------------- | ------ | -------------------------------------- |
| `/api/register/`      | POST   | Register a new user                    |
| `/api/login/`         | POST   | Login and obtain JWT tokens            |
| `/api/logout/`        | POST   | Logout and blacklist the refresh token |
| `/api/token/refresh/` | POST   | Refresh JWT access token               |

### Quiz App

| Endpoint             | Method | Description                      |
| -------------------- | ------ | -------------------------------- |
| `/api/createQuiz/`   | POST   | Create a new quiz                |
| `/api/quizzes/`      | GET    | List all quizzes                 |
| `/api/quizzes/{id}/` | GET    | Retrieve a specific quiz         |
| `/api/quizzes/{id}/` | PUT    | Update a specific quiz           |
| `/api/quizzes/{id}/` | PATCH  | Partially update a specific quiz |
| `/api/quizzes/{id}/` | DELETE | Delete a specific quiz           |

---
