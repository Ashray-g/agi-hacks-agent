# Conflict Resolver

A comprehensive calendar management system that extracts events from text messages, adds them to your calendar, and intelligently resolves scheduling conflicts.

## Overview

Conflict Resolver is a personalized agent= designed to streamline your calendar management by:

1. Extracting event information from natural language text
2. Adding these events to your calendar
3. Detecting and resolving conflicts with existing calendar events
4. Finding free time slots in your schedule

The system integrates with your existing calendar (via iCalendar) and uses agents to parse event details from text, making it easy to schedule events from emails, messages, or notes.

## Features

- **Natural Language Processing**: Extract event details (title, time, location, etc.) from plain text using AI
- **Calendar Integration**: Sync with your existing calendar via iCalendar
- **Conflict Detection**: Automatically identify scheduling conflicts between new and existing events
- **Free Time Finder**: Discover available time slots in your schedule
- **JSON Storage**: Store events in a structured format for easy access and manipulation

## Components

### Core Files

- `add_event.py`: Parses natural language text into structured event data and adds it to your calendar
- `conflict-detect.py`: Identifies scheduling conflicts between events
- `free-times.py`: Finds available time slots in your schedule
- `events.py`: Fetches and processes events from your iCalendar
- `model.py`: Interfaces with the Groq AI model for natural language processing

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/conflict-resolver.git
   cd conflict-resolver
   ```

2. Install dependencies:
   ```
   pip install pytz icalevents groq
   ```

3. Set up your API key:
   Create a `.env` file with your Groq API key:
   ```
   groq_api_key=your_api_key_here
   ```

4. Configure your calendar:
   Update the iCalendar URL in `events.py` to point to your calendar.

## Usage

### Adding Events from Text

```python
from add_event import add_event_from_text

# Add an event using natural language
add_event_from_text("Meeting with John tomorrow from 2pm to 3pm at Conference Room A")
```

## Dependencies

- Python 3.6+
- pytz
- icalevents
- groq

## License

[MIT License](LICENSE)
