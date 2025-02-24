import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain.prompts import PromptTemplate
import cohere

# Define Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def load_text_file(file_id):
    """Loads text from a Google Drive file given its ID."""
    creds = None
    
    # Check if token.json exists for authentication
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('Credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Build the Drive service
    service = build('drive', 'v3', credentials=creds)
    request = service.files().get_media(fileId=file_id)
    file_data = request.execute()
    
    return file_data.decode('utf-8')

# Load Cohere API Key
api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise ValueError("COHERE_API_KEY environment variable not set.")
co = cohere.Client(api_key)

# Sample prompt template
template = """
Summarize the following text in a concise manner:
{text_content}

Summary:
"""

# Create a prompt template
prompt = PromptTemplate(
    input_variables=["text_content"],
    template=template,
)

if __name__ == '__main__':
    # Replace with your actual Google Drive file ID
    FILE_ID = '16xKiK92UPVhXEc0SaCt4oYjAbitpGfRc'
    
    # Load text from Google Drive
    try:
        text_content = load_text_file(FILE_ID)
    except Exception as e:
        print(f"Error loading file: {e}")
        exit()
    
    # Format the prompt
    formatted_prompt = prompt.format(text_content=text_content)
    
    # Use Cohere to generate a response
    response = co.generate(
        model='command',
        prompt=formatted_prompt,
        max_tokens=100,
        temperature=0.5
    )
    
    # Display the output
    print("Output:", response.generations[0].text)
