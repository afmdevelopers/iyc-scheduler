from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import shutil
from pathlib import Path
import re
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Define models for data validation
class Event(BaseModel):
    time: str
    name: str
    link: Optional[str] = None
    hasOutline: Optional[bool] = False
    outlineFile: Optional[str] = None

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
UPLOADS_DIR = Path("./uploads")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount the uploads directory to make files accessible
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
    return {"message": "International Youth Conference Schedule API"}

@app.get("/api/schedule")
def get_schedule():
    logger.info("Getting schedule")
    return read_schedule()

@app.post("/api/schedule/day")
def add_day(day_data: DayCreate):
    logger.info(f"Adding day: {day_data.day}")
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
    logger.info(f"Adding event: {event_data.name} to day {event_data.day_id}")
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

# New endpoints for file upload
@app.post("/api/schedule/event/upload")
async def upload_event_with_file(
    day_id: str = Form(...),
    time: str = Form(...),
    name: str = Form(...),
    link: Optional[str] = Form(None),
    hasOutline: bool = Form(False),
    file: Optional[UploadFile] = File(None)
):
    logger.info(f"Adding event with file: {name} to day {day_id}")
    schedule = read_schedule()
    
    # Find the day by ID
    day_found = False
    for day in schedule:
        if day["id"] == day_id:
            day_found = True
            
            # Check if event with same name already exists
            for event in day["events"]:
                if event["name"] == name:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Event with name '{name}' already exists for {day['day']}"
                    )
            
            # Generate a simple ID for the event
            event_id = generate_event_id(day["id"], name)
            
            # Create event dict with only non-None values
            event_dict = {
                "id": event_id,
                "time": time,
                "name": name
            }
            
            if link:
                event_dict["link"] = link
            
            outlineFile = None
            
            # Handle file upload if provided
            if file and hasOutline:
                logger.info(f"Processing file {file.filename} for event {name}")
                # Create an event-specific directory for the file
                event_dir = UPLOADS_DIR / event_id
                os.makedirs(event_dir, exist_ok=True)
                
                # Save the file with its original name
                file_path = event_dir / file.filename
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                
                # Update the event with the file path
                outlineFile = f"/uploads/{event_id}/{file.filename}"
                event_dict["hasOutline"] = True
                event_dict["outlineFile"] = outlineFile
            elif hasOutline:
                event_dict["hasOutline"] = True
            
            # Add event to the day
            day["events"].append(event_dict)
            break
    
    if not day_found:
        raise HTTPException(status_code=404, detail=f"Day with ID '{day_id}' not found")
    
    write_schedule(schedule)
    return schedule

@app.put("/api/schedule/event/{day_id}/{event_id}")
def update_event(day_id: str, event_id: str, event: Event):
    logger.info(f"Updating event: {event_id} for day {day_id}")
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
                    
                    # Keep the existing outline file if it exists
                    if "outlineFile" in existing_event and event.hasOutline:
                        event_dict["outlineFile"] = existing_event["outlineFile"]
                    
                    # If outline file is specifically provided, use it
                    if event.outlineFile:
                        event_dict["outlineFile"] = event.outlineFile
                    
                    # Update event
                    day["events"][i] = event_dict
                    
                    # If the ID changed (due to name change), we might need to move any uploaded files
                    if new_event_id != event_id and "outlineFile" in event_dict:
                        old_dir = UPLOADS_DIR / event_id
                        new_dir = UPLOADS_DIR / new_event_id
                        
                        if old_dir.exists():
                            # Create new directory
                            os.makedirs(new_dir, exist_ok=True)
                            
                            # Move files from old to new directory
                            for file_path in old_dir.glob("*"):
                                shutil.move(str(file_path), str(new_dir / file_path.name))
                            
                            # Update the file path in the event
                            if event_dict["outlineFile"]:
                                old_path = event_dict["outlineFile"]
                                filename = old_path.split("/")[-1]
                                event_dict["outlineFile"] = f"/uploads/{new_event_id}/{filename}"
                            
                            # Remove the old directory if it's empty
                            try:
                                os.rmdir(old_dir)
                            except OSError:
                                pass
                    
                    break
            
            if not event_found:
                raise HTTPException(status_code=404, detail=f"Event with ID '{event_id}' not found")
            
            break
    
    if not day_found:
        raise HTTPException(status_code=404, detail=f"Day with ID '{day_id}' not found")
    
    write_schedule(schedule)
    return schedule

@app.post("/api/schedule/event/{day_id}/{event_id}/upload")
async def upload_outline(
    day_id: str,
    event_id: str,
    file: UploadFile = File(...)
):
    logger.info(f"Uploading outline for event: {event_id} in day {day_id}")
    try:
        logger.info(f"File details: name={file.filename}, content_type={file.content_type}")
        schedule = read_schedule()
        
        # Find the day by ID
        day_found = False
        for day in schedule:
            if day["id"] == day_id:
                day_found = True
                
                # Find the event by ID
                event_found = False
                for i, event in enumerate(day["events"]):
                    if event["id"] == event_id:
                        event_found = True
                        
                        # Create an event-specific directory for the file
                        event_dir = UPLOADS_DIR / event_id
                        os.makedirs(event_dir, exist_ok=True)
                        
                        # Save the file with its original name
                        file_path = event_dir / file.filename
                        logger.info(f"Saving file to {file_path}")
                        with open(file_path, "wb") as f:
                            content = await file.read()
                            f.write(content)
                        
                        # Update the event with the file path and hasOutline flag
                        event["hasOutline"] = True
                        event["outlineFile"] = f"/uploads/{event_id}/{file.filename}"
                        break
                
                if not event_found:
                    logger.error(f"Event with ID '{event_id}' not found")
                    raise HTTPException(status_code=404, detail=f"Event with ID '{event_id}' not found")
                
                break
        
        if not day_found:
            logger.error(f"Day with ID '{day_id}' not found")
            raise HTTPException(status_code=404, detail=f"Day with ID '{day_id}' not found")
        
        write_schedule(schedule)
        return schedule
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.delete("/api/schedule/event/{day_id}/{event_id}")
def delete_event(day_id: str, event_id: str):
    logger.info(f"Deleting event: {event_id} from day {day_id}")
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
                    
                    # Delete any uploaded files for this event
                    event_dir = UPLOADS_DIR / event_id
                    if event_dir.exists():
                        shutil.rmtree(event_dir)
                    
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
    logger.info(f"Deleting day: {day_id}")
    schedule = read_schedule()
    
    # Find the day by ID
    day_found = False
    for i, day in enumerate(schedule):
        if day["id"] == day_id:
            day_found = True
            
            # Delete any uploaded files for all events in this day
            for event in day["events"]:
                event_dir = UPLOADS_DIR / event["id"]
                if event_dir.exists():
                    shutil.rmtree(event_dir)
            
            # Delete day
            schedule.pop(i)
            break
    
    if not day_found:
        raise HTTPException(status_code=404, detail=f"Day with ID '{day_id}' not found")
    
    write_schedule(schedule)
    return schedule

@app.post("/api/schedule/initialize")
def initialize_schedule():
    logger.info("Initializing sample schedule")
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


# Run the application with: uvicorn main:app --reload --port 6000
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IYC Schedule API")
    parser.add_argument('--port', type=int, default=6000, help='Port to run the server on')
    args = parser.parse_args()
    
    # Get port from environment variable or use command line argument
    port = int(os.environ.get("PORT", args.port))
    
    import uvicorn
    print(f"Starting Youth Conference Schedule API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)