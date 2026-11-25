import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from config import SERVICE_ACCOUNT_FILE, RAW_DIR

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
GSHEET_MIME = 'application/vnd.google-apps.spreadsheet'

def get_service():
    creds = service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE), scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)

def list_files(service, folder_id):
    query = "'%s' in parents and trashed = false" % folder_id
    files, page_token = [], None
    while True:
        resp = service.files().list(
            q=query,
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token,
        ).execute()
        files.extend(resp.get('files', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            return files

def download_file(service, file):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    name = file['name']
    if file['mimeType'] == GSHEET_MIME:
        request = service.files().export_media(fileId=file['id'], mimeType='text/csv')
        name += '.csv'
    else:
        request = service.files().get_media(fileId=file['id'])
    path = RAW_DIR / name
    with io.FileIO(path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return path