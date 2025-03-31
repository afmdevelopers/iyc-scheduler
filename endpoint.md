# API Sample Data with Simple IDs

This document provides sample data for all API endpoints, demonstrating how the IDs are generated from day numbers and event names.

## 1. GET /api/schedule - Get all schedule data

**Response:**
```json
[
  {
    "id": "1",
    "day": "Day 1",
    "date": "WEDNESDAY, 27TH DECEMBER 2023",
    "events": [
      {
        "id": "1-arrival-of-participants",
        "time": "12:00pm - 4:00pm (GMT +1)",
        "name": "Arrival of Participants"
      },
      {
        "id": "1-welcome-programme-movie-premiere",
        "time": "7:30pm - 10:30pm (GMT +1)",
        "name": "Welcome programme / Movie Premiere",
        "link": "https://www.youtube.com/live/kbTISnzSoeA?feature=shared"
      }
    ]
  },
  {
    "id": "2",
    "day": "Day 2",
    "date": "THURSDAY, 28TH DECEMBER 2023",
    "events": [
      {
        "id": "2-p-u-s-h",
        "time": "5:30am - 7:00am (GMT +1)",
        "name": "P.U.S.H",
        "link": "https://www.youtube.com/live/rnCSGMtxhSc?feature=shared"
      },
      {
        "id": "2-bible-study",
        "time": "9:30pm - 12:00pm (GMT +1)",
        "name": "Bible Study",
        "link": "https://www.youtube.com/live/dE3PmH2-JHg?feature=shared",
        "hasOutline": true
      }
    ]
  }
]
```

## 2. POST /api/schedule/day - Add a new day

**Request:**
```json
{
  "day": "Day 4",
  "date": "SATURDAY, 30TH DECEMBER 2023"
}
```

**Response:**
```json
[
  {
    "id": "1",
    "day": "Day 1",
    "date": "WEDNESDAY, 27TH DECEMBER 2023",
    "events": [...]
  },
  // Other existing days...
  {
    "id": "4",
    "day": "Day 4",
    "date": "SATURDAY, 30TH DECEMBER 2023",
    "events": []
  }
]
```

Notice how the `id` for the day is automatically set to `"4"` based on the day number.

## 3. POST /api/schedule/event - Add a new event to a day

**Request:**
```json
{
  "day_id": "4",
  "time": "10:00am - 12:00pm (GMT +1)",
  "name": "Closing Ceremony",
  "link": "https://www.youtube.com/live/example123?feature=shared",
  "hasOutline": true
}
```

**Response:**
```json
[
  // Previous days...
  {
    "id": "4",
    "day": "Day 4",
    "date": "SATURDAY, 30TH DECEMBER 2023",
    "events": [
      {
        "id": "4-closing-ceremony",
        "time": "10:00am - 12:00pm (GMT +1)",
        "name": "Closing Ceremony",
        "link": "https://www.youtube.com/live/example123?feature=shared",
        "hasOutline": true
      }
    ]
  }
]
```

Notice how the event ID is generated as `"4-closing-ceremony"`, combining the day ID and a slug of the event name.

## 4. PUT /api/schedule/event/{day_id}/{event_id} - Update an existing event

**URL:** `/api/schedule/event/4/4-closing-ceremony`

**Request:**
```json
{
  "time": "11:00am - 1:00pm (GMT +1)",
  "name": "Closing Ceremony and Awards",
  "link": "https://www.youtube.com/live/updated123?feature=shared",
  "hasOutline": true
}
```

**Response:**
```json
[
  // Previous days...
  {
    "id": "4",
    "day": "Day 4",
    "date": "SATURDAY, 30TH DECEMBER 2023",
    "events": [
      {
        "id": "4-closing-ceremony-and-awards",
        "time": "11:00am - 1:00pm (GMT +1)",
        "name": "Closing Ceremony and Awards",
        "link": "https://www.youtube.com/live/updated123?feature=shared",
        "hasOutline": true
      }
    ]
  }
]
```

Notice how the event ID is automatically updated to `"4-closing-ceremony-and-awards"` when the name changes.

## 5. DELETE /api/schedule/event/{day_id}/{event_id} - Delete an event

**URL:** `/api/schedule/event/4/4-closing-ceremony-and-awards`

**Response:**
```json
[
  // Previous days...
  {
    "id": "4",
    "day": "Day 4",
    "date": "SATURDAY, 30TH DECEMBER 2023",
    "events": []
  }
]
```

## 6. DELETE /api/schedule/day/{day_id} - Delete a day

**URL:** `/api/schedule/day/4`

**Response:**
```json
[
  {
    "id": "1",
    "day": "Day 1",
    "date": "WEDNESDAY, 27TH DECEMBER 2023",
    "events": [...]
  },
  {
    "id": "2",
    "day": "Day 2",
    "date": "THURSDAY, 28TH DECEMBER 2023",
    "events": [...]
  },
  {
    "id": "3",
    "day": "Day 3",
    "date": "FRIDAY, 29TH DECEMBER 2023",
    "events": [...]
  }
]
```

## 7. POST /api/schedule/initialize - Initialize with sample data

This is a POST request with no body required.

**Response:**
```json
[
  {
    "id": "1",
    "day": "Day 1",
    "date": "WEDNESDAY, 27TH DECEMBER 2023", 
    "events": [
      {
        "id": "1-arrival-of-participants",
        "time": "12:00pm - 4:00pm (GMT +1)",
        "name": "Arrival of Participants"
      },
      {
        "id": "1-welcome-programme-movie-premiere",
        "time": "7:30pm - 10:30pm (GMT +1)",
        "name": "Welcome programme / Movie Premiere",
        "link": "https://www.youtube.com/live/kbTISnzSoeA?feature=shared"
      }
    ]
  },
  {
    "id": "2",
    "day": "Day 2",
    "date": "THURSDAY, 28TH DECEMBER 2023",
    "events": [
      {
        "id": "2-p-u-s-h",
        "time": "5:30am - 7:00am (GMT +1)",
        "name": "P.U.S.H",
        "link": "https://www.youtube.com/live/rnCSGMtxhSc?feature=shared"
      },
      {
        "id": "2-bible-study",
        "time": "9:30pm - 12:00pm (GMT +1)",
        "name": "Bible Study",
        "link": "https://www.youtube.com/live/dE3PmH2-JHg?feature=shared",
        "hasOutline": true
      }
    ]
  },
  {
    "id": "3",
    "day": "Day 3",
    "date": "FRIDAY, 29TH DECEMBER 2023",
    "events": [
      {
        "id": "3-p-u-s-h",
        "time": "5:30 - 7:00 (GMT +1)",
        "name": "P.U.S.H",
        "link": "https://www.youtube.com/live/Sr5SvTBszlI?feature=shared"
      },
      {
        "id": "3-symposium-aspire",
        "time": "09:30am - 12:00pm (GMT +1)",
        "name": "Symposium - ASPIRE",
        "hasOutline": true,
        "link": "https://www.youtube.com/live/ZrHCG-1KUjo?feature=shared"
      }
    ]
  }
]
```

## Testing with curl

Here are curl commands for testing each endpoint:

1. **Get schedule:**
   ```bash
   curl -X GET http://localhost:8000/api/schedule
   ```

2. **Add a day:**
   ```bash
   curl -X POST http://localhost:8000/api/schedule/day \
     -H "Content-Type: application/json" \
     -d '{"day": "Day 4", "date": "SATURDAY, 30TH DECEMBER 2023"}'
   ```

3. **Add an event:**
   ```bash
   curl -X POST http://localhost:8000/api/schedule/event \
     -H "Content-Type: application/json" \
     -d '{"day_id": "4", "time": "10:00am - 12:00pm (GMT +1)", "name": "Closing Ceremony", "link": "https://www.youtube.com/live/example123?feature=shared", "hasOutline": true}'
   ```

4. **Update an event:**
   ```bash
   curl -X PUT "http://localhost:8000/api/schedule/event/4/4-closing-ceremony" \
     -H "Content-Type: application/json" \
     -d '{"time": "11:00am - 1:00pm (GMT +1)", "name": "Closing Ceremony and Awards", "link": "https://www.youtube.com/live/updated123?feature=shared", "hasOutline": true}'
   ```

5. **Delete an event:**
   ```bash
   curl -X DELETE "http://localhost:8000/api/schedule/event/4/4-closing-ceremony-and-awards"
   ```

6. **Delete a day:**
   ```bash
   curl -X DELETE "http://localhost:8000/api/schedule/day/4"
   ```

7. **Initialize with sample data:**
   ```bash
   curl -X POST http://localhost:8000/api/schedule/initialize
   ```