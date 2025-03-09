import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from google.auth.transport.requests import Request
import pickle
from email.message import EmailMessage

# Load environment variables from .env file
load_dotenv()

# Define the scopes you need
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    # Token file to store credentials
    token_file = 'token.pickle'
    
    try:
        # Try to load existing credentials
        if os.path.exists(token_file):
            print("Loading existing credentials")
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials available, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', 
                    SCOPES,
                    redirect_uri='http://localhost:8080'
                )
                creds = flow.run_local_server(
                    port=8080,
                    prompt='consent'
                )
            # Save the credentials for future use
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build the Gmail service
        service = build('gmail', 'v1', credentials=creds)
        print("Gmail service initialized successfully")
        return service
    except Exception as e:
        print(f"Error initializing Gmail service: {str(e)}")
        raise


def create_draft(service, to, subject, body, from_email=None):
    try:
        # Create a message
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        if from_email:
            message["From"] = from_email
        message["Subject"] = subject
        
        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Create the draft
        create_message = {"message": {"raw": encoded_message}}
        draft = service.users().drafts().create(userId="me", body=create_message).execute()
        
        print(f'Draft created successfully! Draft ID: {draft["id"]}')
        return draft
    
    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def send_email(service, to, subject, body, from_email=None):
    try:
        # Create a message
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        if from_email:
            message["From"] = from_email
        message["Subject"] = subject
        
        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send the message
        create_message = {"raw": encoded_message}
        sent_message = service.users().messages().send(userId="me", body=create_message).execute()
        
        print(f'Message sent successfully! Message ID: {sent_message["id"]}')
        return sent_message
    
    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def reply_to_email(service, message_id, to, subject, body, from_email=None):
    try:
        # Get the original message to extract necessary headers
        original_message = service.users().messages().get(userId="me", id=message_id, format="metadata", 
                                                         metadataHeaders=["Subject", "References", "Message-ID", "Thread-Index"]).execute()
        thread_id = original_message['threadId']
        
        # Extract headers from original message
        headers = original_message['payload']['headers']
        original_subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        original_message_id = next((h['value'] for h in headers if h['name'] == 'Message-ID'), f"<{message_id}@mail.gmail.com>")
        references = next((h['value'] for h in headers if h['name'] == 'References'), '')
        
        # Create a message
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        if from_email:
            message["From"] = from_email
            
        # Ensure we keep the exact same subject as the original for better Outlook threading
        message["Subject"] = original_subject
        
        # Set threading headers in specific order for Outlook
        message["Thread-Index"] = thread_id  # Add Thread-Index for Outlook
        message["In-Reply-To"] = original_message_id
        message["References"] = f"{references} {original_message_id}".strip()
        
        # Add these Outlook-specific headers
        message["Thread-Topic"] = original_subject.replace("Re: ", "").strip()
        message["Thread-Parent"] = original_message_id
        
        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send the message in the same thread
        create_message = {
            "raw": encoded_message,
            "threadId": thread_id
        }
        
        sent_message = service.users().messages().send(userId="me", body=create_message).execute()
        
        print(f'Reply sent successfully! Message ID: {sent_message["id"]}')
        return sent_message
    
    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def read_emails(service, max_results=10, query=None, include_body=True):
    try:
        # Get list of messages
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        if not messages:
            print("No messages found.")
            return []
            
        emails = []
        
        # Process each message
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            
            # Extract email details
            headers = msg["payload"]["headers"]
            email_data = {
                "id": msg["id"],
                "threadId": msg["threadId"],
                "labelIds": msg["labelIds"],
                "snippet": msg["snippet"],
            }
            
            # Extract headers
            for header in headers:
                if header["name"].lower() == "from":
                    email_data["from"] = header["value"]
                elif header["name"].lower() == "to":
                    email_data["to"] = header["value"]
                elif header["name"].lower() == "subject":
                    email_data["subject"] = header["value"]
                elif header["name"].lower() == "date":
                    email_data["date"] = header["value"]
            
            # Include full message payload if requested
            if include_body:
                email_data["payload"] = msg["payload"]
            
            emails.append(email_data)
        
        print(f"Successfully retrieved {len(emails)} recent emails.")
        return emails
        
    except Exception as error:
        print(f"An error occurred: {error}")
        return []
