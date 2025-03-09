import json
from datetime import datetime
import pytz

def load_events(file_path):
    """
    Load events from a JSON file
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading events from {file_path}: {e}")
        return []

def parse_datetime(dt_string):
    """
    Parse datetime string to datetime object
    """
    if dt_string is None:
        return None
    
    # Handle ISO format with or without timezone
    try:
        dt = datetime.fromisoformat(dt_string)
        # If the datetime is naive (no timezone), make it timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pytz.UTC)
        return dt
    except ValueError:
        # Try without the 'Z' if present
        if dt_string.endswith('Z'):
            dt = datetime.fromisoformat(dt_string[:-1])
            # Add UTC timezone
            dt = dt.replace(tzinfo=pytz.UTC)
            return dt
        raise

def check_time_conflict(event1, event2):
    """
    Check if two events have conflicting times
    """
    try:
        # Parse start and end times
        start1 = parse_datetime(event1.get('start'))
        end1 = parse_datetime(event1.get('end'))
        start2 = parse_datetime(event2.get('start'))
        end2 = parse_datetime(event2.get('end'))
        
        # Skip if any datetime is None
        if None in (start1, end1, start2, end2):
            return False
        
        # Check for overlap
        return (start1 < end2 and start2 < end1)
    except Exception as e:
        print(f"Error checking conflict: {e}")
        return False

def detect_conflicts():
    """
    Detect conflicts between events in future-events.json and shadow-events.json
    """
    future_events = load_events("future-events.json")
    shadow_events = load_events("shadow-events.json")
    
    conflicts = []
    
    # Compare each future event with each shadow event
    for future_event in future_events:
        for shadow_event in shadow_events:
            if check_time_conflict(future_event, shadow_event):
                conflicts.append({
                    "future_event": future_event["title"],
                    "shadow_event": shadow_event["title"],
                    "future_time": f"{future_event['start']} to {future_event['end']}",
                    "shadow_time": f"{shadow_event['start']} to {shadow_event['end']}"
                })
    
    # Print conflicts
    if conflicts:
        print(f"Found {len(conflicts)} conflicts:")
        for i, conflict in enumerate(conflicts, 1):
            print(f"\nConflict #{i}:")
            print(f"  '{conflict['future_event']}' conflicts with '{conflict['shadow_event']}'")
            print(f"  Future event time: {conflict['future_time']}")
            print(f"  Shadow event time: {conflict['shadow_time']}")
    else:
        print("No conflicts found.")
    
    return conflicts

if __name__ == "__main__":
    detect_conflicts()
