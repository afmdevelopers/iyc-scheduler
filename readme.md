# FastAPI Backend Setup Instructions

This document explains how to set up and run the FastAPI backend for your Youth Conference Schedule Manager.

## Prerequisites

- Python 3.7+ installed
- pip (Python package manager)

## Step 1: Create a Virtual Environment

It's recommended to create a virtual environment to isolate the dependencies:

```bash
# Create a new directory for your project
mkdir youth-conference-api
cd youth-conference-api

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

## Step 2: Install Dependencies

Install FastAPI and its dependencies:

```bash
pip install fastapi uvicorn pydantic
```

## Step 3: Create the FastAPI Application

Create a file named `main.py` with the FastAPI code provided in the artifacts.

## Step 4: Create a Data Directory

```bash
mkdir -p data
```

## Step 4.1: Create an Uploads Directory

```bash
mkdir -p uploads
```

## Step 5: Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-reloading when you make changes to the code, which is useful during development.

Your API will be available at:
- API endpoints: http://localhost:8000/api/...
- Interactive API documentation: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint                            | Description                     |
|--------|-------------------------------------|---------------------------------|
| GET    | /api/schedule                       | Get all schedule data           |
| POST   | /api/schedule/day                   | Add a new day                   |
| POST   | /api/schedule/event                 | Add a new event to a day        |
| PUT    | /api/schedule/event/{day_index}/{event_index} | Update an existing event  |
| DELETE | /api/schedule/event/{day_index}/{event_index} | Delete an event           |
| DELETE | /api/schedule/day/{day_index}       | Delete a day                    |
| POST   | /api/schedule/initialize            | Initialize with sample data     |

## Testing the API

You can test the API using the interactive documentation provided by FastAPI at `http://localhost:8000/docs`.

Alternatively, you can use tools like curl or Postman to make HTTP requests to the API endpoints.

Example: Initialize the schedule with sample data:

```bash
curl -X POST http://localhost:8000/api/schedule/initialize
```

## Integrating with the Frontend

Update the API_URL in your frontend code to point to your FastAPI backend:

```javascript
const API_URL = 'http://localhost:8000/api';
```

## Deployment

production deployment command:

```bash
pm2 start ecosystem.config.js
```

