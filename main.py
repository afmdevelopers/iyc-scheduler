from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from pathlib import Path
import re
import argparse

# Define models for data validation
class Event(BaseModel):
    time: str
    name: str
    link: Optional[str] = None
    hasOutline: Optional[bool] = False

class DayCreate(BaseModel):
    day: str
    date: str

class EventCreate(BaseModel):
    day_id: str
    time: str
    name: str
    link: Optional[str] = None
    hasOutline: Optional[bool] = False

class Day(BaseModel):
    id: str
    day: str
    date: str
    events: List[Event] = []

# Create FastAPI app
app = FastAPI(title="Youth Conference Schedule API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File path for storing schedule data
DATA_DIR = Path("./data")
SCHEDULE_FILE = DATA_DIR / "schedule.json"

# Generate a simple ID from a day string (e.g., "Day 1" -> "1")
def generate_day_id(day_str):
    # Extract the last part of the day string, which should be the number
    match = re.search(r'(\d+)$', day_str)
    if match:
        return match.group(1)
    else:
        # Fallback to a simple sanitized version of the string
        return re.sub(r'[^a-zA-Z0-9]', '', day_str).lower()

# Generate a simple ID for an event (e.g., day_id="1", event_name="Bible Study" -> "1-bible-study")
def generate_event_id(day_id, event_name):
    # Create a slug from the event name
    event_slug = re.sub(r'[^a-zA-Z0-9]', '-', event_name.lower())
    event_slug = re.sub(r'-+', '-', event_slug)  # Replace multiple hyphens with a single one
    event_slug = event_slug.strip('-')  # Remove leading/trailing hyphens
    
    return f"{day_id}-{event_slug}"

# Initialize data directory and schedule file if they don't exist
def initialize_data_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not SCHEDULE_FILE.exists():
        with open(SCHEDULE_FILE, "w") as f:
            json.dump([], f)

# Helper function to read schedule data
def read_schedule():
    initialize_data_file()
    
    with open(SCHEDULE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Return empty schedule if file is empty or corrupted
            return []

# Helper function to write schedule data
def write_schedule(schedule):
    initialize_data_file()
    
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule, f, indent=2)

# API routes
@app.get("/")
def read_root():
    return {"message": "Youth Conference Schedule API"}

@app.get("/api/schedule")
def get_schedule():
    return read_schedule()

@app.post("/api/schedule/day")
def add_day(day_data: DayCreate):
    schedule = read_schedule()
    
    # Check if day already exists
    for day in schedule:
        if day["day"] == day_data.day or day["date"] == day_data.date:
            raise HTTPException(status_code=400, detail="This day or date already exists in the schedule")
    
    # Generate a simple ID for the day
    day_id = generate_day_id(day_data.day)
    
    # Add new day
    schedule.append({
        "id": day_id,
        "day": day_data.day,
        "date": day_data.date,
        "events": []
    })
    
    write_schedule(schedule)
    return schedule

@app.post("/api/schedule/event")
def add_event(event_data: EventCreate):
    schedule = read_schedule()
    
    # Find the day by ID
    day_found = False
    for day in schedule:
        if day["id"] == event_data.day_id:
            day_found = True
            
            # Check if event with same name already exists
            for event in day["events"]:
                if event["name"] == event_data.name:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Event with name '{event_data.name}' already exists for {day['day']}"
                    )
            
            # Generate a simple ID for the event
            event_id = generate_event_id(day["id"], event_data.name)
            
            # Create event dict with only non-None values
            event_dict = {
                "id": event_id,
                "time": event_data.time,
                "name": event_data.name
            }
            
            if event_data.link:
                event_dict["link"] = event_data.link
                
            if event_data.hasOutline:
                event_dict["hasOutline"] = event_data.hasOutline
            
            # Add event to the day
            day["events"].append(event_dict)
            break
    
    if not day_found:
        raise HTTPException(status_code=404, detail=f"Day with ID '{event_data.day_id}' not found")
    
    write_schedule(schedule)
    return schedule

@app.put("/api/schedule/event/{day_id}/{event_id}")
def update_event(day_id: str, event_id: str, event: Event):
    schedule = read_schedule()
    
    # Find the day by ID
    day_found = False
    for day in schedule:
        if day["id"] == day_id:
            day_found = True
            
            # Find the event by ID
            event_found = False
            for i, existing_event in enumerate(day["events"]):
                if existing_event["id"] == event_id:
                    event_found = True
                    
                    # Check if new name conflicts with another event (if name is being changed)
                    if existing_event["name"] != event.name:
                        for other_event in day["events"]:
                            if other_event["name"] == event.name and other_event != existing_event:
                                raise HTTPException(
                                    status_code=400,
                                    detail=f"Event with name '{event.name}' already exists for {day['day']}"
                                )
                    
                    # Generate a new ID if the name changes
                    new_event_id = event_id
                    if existing_event["name"] != event.name:
                        new_event_id = generate_event_id(day["id"], event.name)
                    
                    # Create event dict with only non-None values
                    event_dict = {
                        "id": new_event_id,
                        "time": event.time,
                        "name": event.name
                    }
                    
                    if event.link:
                        event_dict["link"] = event.link
                        
                    if event.hasOutline:
                        event_dict["hasOutline"] = event.hasOutline
                    
                    # Update event
                    day["events"][i] = event_dict
                    break
            
            if not event_found:
                raise HTTPException(status_code=404, detail=f"Event with ID '{event_id}' not found")
            
            break
    
    if not day_found:
        raise HTTPException(status_code=404, detail=f"Day with ID '{day_id}' not found")
    
    write_schedule(schedule)
    return schedule

@app.delete("/api/schedule/event/{day_id}/{event_id}")
def delete_event(day_id: str, event_id: str):
    schedule = read_schedule()
    
    # Find the day by ID
    day_found = False
    for day in schedule:
        if day["id"] == day_id:
            day_found = True
            
            # Find the event by ID
            event_found = False
            for i, existing_event in enumerate(day["events"]):
                if existing_event["id"] == event_id:
                    event_found = True
                    # Delete event
                    day["events"].pop(i)
                    break
            
            if not event_found:
                raise HTTPException(status_code=404, detail=f"Event with ID '{event_id}' not found")
            
            break
    
    if not day_found:
        raise HTTPException(status_code=404, detail=f"Day with ID '{day_id}' not found")
    
    write_schedule(schedule)
    return schedule

@app.delete("/api/schedule/day/{day_id}")
def delete_day(day_id: str):
    schedule = read_schedule()
    
    # Find the day by ID
    day_found = False
    for i, day in enumerate(schedule):
        if day["id"] == day_id:
            day_found = True
            # Delete day
            schedule.pop(i)
            break
    
    if not day_found:
        raise HTTPException(status_code=404, detail=f"Day with ID '{day_id}' not found")
    
    write_schedule(schedule)
    return schedule

@app.post("/api/schedule/initialize")
def initialize_schedule():
    # Sample schedule data with auto-generated IDs
    sample_days = [
        {
            "day": "Day 1",
            "date": "WEDNESDAY, 27TH DECEMBER 2023", 
            "events": [
                {
                    "time": "12:00pm - 4:00pm (GMT +1)",
                    "name": "Arrival of Participants"
                },
                {
                    "time": "7:30pm - 10:30pm (GMT +1)",
                    "name": "Welcome programme / Movie Premiere",
                    "link": "https://www.youtube.com/live/kbTISnzSoeA?feature=shared"
                }
            ]
        },
        {
            "day": "Day 2",
            "date": "THURSDAY, 28TH DECEMBER 2023",
            "events": [
                {
                    "time": "5:30am - 7:00am (GMT +1)",
                    "name": "P.U.S.H",
                    "link": "https://www.youtube.com/live/rnCSGMtxhSc?feature=shared"
                },
                {
                    "time": "9:30pm - 12:00pm (GMT +1)",
                    "name": "Bible Study",
                    "link": "https://www.youtube.com/live/dE3PmH2-JHg?feature=shared",
                    "hasOutline": True
                }
            ]
        },
        {
            "day": "Day 3",
            "date": "FRIDAY, 29TH DECEMBER 2023",
            "events": [
                {
                    "time": "5:30 - 7:00 (GMT +1)",
                    "name": "P.U.S.H",
                    "link": "https://www.youtube.com/live/Sr5SvTBszlI?feature=shared"
                },
                {
                    "time": "09:30am - 12:00pm (GMT +1)",
                    "name": "Symposium - ASPIRE",
                    "hasOutline": True,
                    "link": "https://www.youtube.com/live/ZrHCG-1KUjo?feature=shared"
                }
            ]
        }
    ]
    
    # Add IDs to all items
    sample_schedule = []
    for day_data in sample_days:
        day_id = generate_day_id(day_data["day"])
        day = {
            "id": day_id,
            "day": day_data["day"],
            "date": day_data["date"],
            "events": []
        }
        
        for event_data in day_data["events"]:
            event_id = generate_event_id(day_id, event_data["name"])
            event = {
                "id": event_id,
                "time": event_data["time"],
                "name": event_data["name"]
            }
            
            if "link" in event_data:
                event["link"] = event_data["link"]
                
            if "hasOutline" in event_data and event_data["hasOutline"]:
                event["hasOutline"] = event_data["hasOutline"]
                
            day["events"].append(event)
            
        sample_schedule.append(day)
    
    write_schedule(sample_schedule)
    return sample_schedule


# Run the application with: uvicorn main:app --reload
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IYC Schedule API")
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    args = parser.parse_args()
    
    # Get port from environment variable or use command line argument
    port = int(os.environ.get("PORT", args.port))
    
    import uvicorn
    print(f"Starting Youth Conference Schedule API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)