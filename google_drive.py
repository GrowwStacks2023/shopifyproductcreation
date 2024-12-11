from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging

def setup_google_drive(credentials_path: str):
    logging.info(f"Setting up Google Drive client with credentials from: {credentials_path}")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        service = build('drive', 'v3', credentials=credentials)
        logging.info("Successfully set up Google Drive client")
        return service
    except Exception as e:
        logging.error(f"Failed to setup Google Drive client: {e}")
        raise

def upload_to_drive(service, file_path: str, folder_id: Optional[str] = None) -> str:
    logging.info(f"Uploading file to Google Drive: {file_path}")
    try:
        file_metadata = {'name': os.path.basename(file_path), 'parents': [folder_id] if folder_id else []}
        media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        service.permissions().create(fileId=file['id'], body={'type': 'anyone', 'role': 'reader'}, fields='id').execute()
        logging.info(f"Successfully uploaded file. File ID: {file['id']}")
        return file['webViewLink']
    except Exception as e:
        logging.error(f"Failed to upload file to Google Drive: {e}")
        raise
