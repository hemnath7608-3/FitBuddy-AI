# FitBuddy AI — Complete FastAPI + Gemini Project

FitBuddy is a web application that generates a structured 7-day wellness/activity plan, provides a practical nutrition/recovery tip, stores results in SQLite, and lets the user submit feedback to revise the plan.

## Features

- FastAPI backend
- Jinja2 frontend
- SQLite + SQLAlchemy persistence
- Gemini integration using the current `google-genai` SDK
- Local demo mode without an API key
- 7-day plan generation
- Nutrition/recovery tip
- Feedback-based plan revision
- JSON REST APIs
- All-users/admin view
- Input validation
- Automated tests
- Responsive UI

## Safety

This is a software demonstration for general wellness. It is not medical care and does not diagnose conditions or prescribe treatment. The generated content avoids extreme dieting, rapid weight-loss targets, and unsafe exercise challenges.

## Project structure

```text
FitBuddy-AI/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── gemini_generator.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── schemas.py
│   └── updated_plan.py
├── static/
│   └── style.css
├── templates/
│   ├── index.html
│   ├── result.html
│   └── all_users.html
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## VS Code setup — Windows

Open the `FitBuddy-AI` folder in VS Code, then open **Terminal → New Terminal**.

### 1. Create the virtual environment

```powershell
python -m venv .venv
```

### 2. Activate it

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`.

For a local demo without Gemini:

```env
DEMO_MODE=true
```

For Gemini:

```env
DEMO_MODE=false
GEMINI_API_KEY=your_key_here
```

The API key must stay in `.env`; never commit it to Git.

## Run

```powershell
python -m uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/view-all-users?key=fitbuddy-demo-admin

## Test

```powershell
pytest -q
```

## API endpoints

- `GET /api/health`
- `POST /api/generate`
- `POST /api/feedback`
- `GET /api/users`

The browser UI uses `/generate-workout` and `/submit-feedback`.

## Gemini

The application uses the current Google GenAI Python SDK:

```python
from google import genai
client = genai.Client(api_key="...")
response = client.models.generate_content(...)
```

Models are configured in `.env`, so you can change them without editing Python.

## Troubleshooting

If you see `ModuleNotFoundError`, activate `.venv` and run `pip install -r requirements.txt`.

If port 8000 is busy:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

If Gemini fails, first use `DEMO_MODE=true` to verify the application itself, then check the API key/model configuration.
