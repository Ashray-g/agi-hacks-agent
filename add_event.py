import json
import os
from datetime import datetime, timedelta
from model import generate_text_with_groq

def parse_event_from_text(text):
    """
    parse natural language text into event structure using groq model
    """
    # Get current date and day information
    current_datetime = datetime.now()
    current_date_str = current_datetime.strftime("%Y-%m-%d")
    current_day_str = current_datetime.strftime("%A")
    
    prompt = f"""
    Today is {current_day_str}, {current_date_str}.
    
    Extract event information from the following text and format it as JSON with these fields:
    - title: the event name/title
    - description: any details about the event
    - location: where the event takes place
    - start: start date and time (YYYY-MM-DD HH:MM format)
    - end: end date and time (YYYY-MM-DD HH:MM format)
    - all_day: boolean indicating if it's an all-day event

    text: {text}

    Return only the JSON object without any additional text.
    """
    
    response = generate_text_with_groq(prompt)
    print(response)
    
    try:
        # Extract JSON content between backticks if present
        if "```json" in response and "```" in response.split("```json", 1)[1]:
            json_content = response.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in response and "```" in response.split("```", 1)[1]:
            json_content = response.split("```", 1)[1].split("```", 1)[0].strip()
        else:
            json_content = response.strip()
        
        # parse the response into a python dictionary
        event_data = json.loads(json_content)
        
        # convert date strings to iso format
        if event_data.get('start'):
            try:
                start_dt = datetime.strptime(event_data['start'], "%Y-%m-%d %H:%M")
                event_data['start'] = start_dt.isoformat()
            except ValueError:
                # handle case where date might be in different format
                pass
                
        if event_data.get('end'):
            try:
                end_dt = datetime.strptime(event_data['end'], "%Y-%m-%d %H:%M")
                event_data['end'] = end_dt.isoformat()
            except ValueError:
                # handle case where date might be in different format
                pass
        
        # add additional required fields
        event_data['attendees'] = []
        event_data['categories'] = []
        event_data['status'] = None
        event_data['organizer'] = "None"
        event_data['source'] = 'user_input'
        
        return event_data
    except json.JSONDecodeError:
        print("Error: Could not parse the model's response as JSON")
        return None
    except Exception as e:
        print(f"Error parsing event data: {e}")
        return None

def add_event_to_json(event_data, json_file="future-events.json"):
    """
    add a new event to the json file
    """
    try:
        # check if file exists, if not create it with an empty list
        if not os.path.exists(json_file):
            with open(json_file, "w") as file:
                json.dump([], file)
        
        # read existing events
        with open(json_file, "r") as file:
            events_list = json.load(file)
        
        # add new event
        events_list.append(event_data)
        
        # sort events by start date and time
        events_list.sort(key=lambda x: x['start'] if x['start'] is not None else '')
        
        # write back to file
        with open(json_file, "w") as file:
            json.dump(events_list, file, indent=4)
        
        return True
    except Exception as e:
        print(f"Error adding event to JSON: {e}")
        return False

def add_event_from_text(text):
    """
    main function to add an event from natural language text
    """
    event_data = parse_event_from_text(text)
    
    if event_data:
        success = add_event_to_json(event_data)
        if success:
            print(f"Event '{event_data['title']}' successfully added to future-events.json")
            return True
        else:
            print("Failed to add event to future-events.json")
            return False
    else:
        print("Failed to parse event information from text")
        return False