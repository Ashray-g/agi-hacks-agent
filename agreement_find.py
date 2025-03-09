import json
from message import read_messages
from model import generate_text_with_groq
import argparse
from datetime import datetime
import time
from add_event import add_event_from_text

def analyze_messages_for_agreement(phone_number, n=10):
    """
    Read the last n messages with a given number and analyze if an agreement has been reached on a meeting time.
    
    Args:
        phone_number (str): The phone number to check messages with
        n (int): Number of messages to analyze
        
    Returns:
        dict: JSON-formatted response with agreement information
    """
    # Read the most recent n messages with the phone number
    messages = read_messages(n=n, phone_number=phone_number)
    
    # Sort messages by date (oldest first) to maintain conversation flow
    messages.sort(key=lambda x: x["date"])
    
    # Format messages for LLM analysis
    conversation = []
    for msg in messages:
        sender = "Me" if msg["is_from_me"] else "Contact"
        conversation.append(f"{sender}: {msg['body']}")
    
    conversation_text = "\n".join(conversation)
    
    # Current date for context
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create prompt for the language model
    prompt = f"""
    Today's date is {current_date}.
    
    Analyze the following conversation between two people and determine if they have reached an agreement on when to meet.
    
    Conversation:
    {conversation_text}
    
    Task: Based on this conversation, analyze if there's a clear agreement on a meeting time.
    Return a JSON object with the following structure:
    {{
        "agreement_reached": true/false,
        "meeting_description": "Description of the meeting. eg ("meeting at 5 pm on ___ for x hours (default 1 hour))",
        "confidence": 0-100,
        "reasoning": "Brief explanation of your conclusion",
        "relevant_messages": ["List of key messages that led to this conclusion"]
    }}
    
    If no agreement was reached, set "agreement_reached" to false and "meeting_time" to null.
    If an agreement was reached, set "agreement_reached" to true and provide the exact meeting time.
    Provide a confidence score (0-100) representing how certain you are of your conclusion.
    
    Return ONLY the JSON object without any additional text.
    """
    
    # Use the language model to analyze the conversation
    response = generate_text_with_groq(prompt)
    
    # Parse the JSON response
    try:
        # Extract JSON content between backticks if present
        if "```json" in response and "```" in response.split("```json", 1)[1]:
            json_content = response.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in response and "```" in response.split("```", 1)[1]:
            json_content = response.split("```", 1)[1].split("```", 1)[0].strip()
        else:
            json_content = response.strip()
        
        result = json.loads(json_content)
        return result
    except Exception as e:
        return {
            "error": f"Failed to parse LLM response: {str(e)}",
            "agreement_reached": False,
            "meeting_time": None,
            "confidence": 0,
            "reasoning": "Error in analysis process",
            "relevant_messages": []
        }

def main():
    while True:
        result = analyze_messages_for_agreement("+18147696903", 15)

        if result["agreement_reached"]:
            print(f"Agreement reached: {result['meeting_description']}")
            add_event_from_text(result['meeting_description'])
            break

        time.sleep(2)

if __name__ == "__main__":
    main()