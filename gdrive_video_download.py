import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
import gdrive_videoloader
import argparse

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_video_ids_in_folder(folder_id, verbose=False):
    """Lists all video IDs in a specified Google Drive folder and its subfolders."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    video_ids = []
    folders_stack = [(folder_id, "")]

    while folders_stack:
        current_folder_id, current_path = folders_stack.pop()
        if verbose:
            print(f"[DEBUG] Processing folder: {current_folder_id}")
        page_token = None

        # Query to search for files within the specific folder, with video MIME types or folders
        query = f"'{current_folder_id}' in parents and (mimeType contains 'video' or mimeType = 'application/vnd.google-apps.folder' or mimeType = 'application/vnd.google-apps.shortcut') and trashed=false"
        if verbose:
            print(f"[DEBUG] Query: {query}")

        while True:
            response = service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, shortcutDetails)',
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()

            files = response.get('files', [])
            if verbose:
                print(f"[DEBUG] Found {len(files)} items in response.")
            for file in files:
                if verbose:
                    print(f"[DEBUG] Item: {file.get('name')} | Type: {file.get('mimeType')}")
                if file.get('mimeType') == 'application/vnd.google-apps.folder':
                    if verbose:
                        print(f"[DEBUG] -> Adding subfolder to stack: {file.get('name')}")
                    new_path = os.path.join(current_path, file.get('name'))
                    folders_stack.append((file.get('id'), new_path))
                elif file.get('mimeType') == 'application/vnd.google-apps.shortcut':
                    shortcut_details = file.get('shortcutDetails')
                    if shortcut_details:
                        target_mime_type = shortcut_details.get('targetMimeType')
                        target_id = shortcut_details.get('targetId')
                        if target_mime_type == 'application/vnd.google-apps.folder':
                            if verbose:
                                print(f"[DEBUG] -> Found shortcut to folder. Adding target to stack: {file.get('name')} ({target_id})")
                            new_path = os.path.join(current_path, file.get('name'))
                            folders_stack.append((target_id, new_path))
                        elif target_mime_type and 'video' in target_mime_type:
                            print(f"Found shortcut to video: {file.get('name')} ({target_id})")
                            video_ids.append({'id': target_id, 'name': file.get('name'), 'path': current_path})
                else:
                    print(f"Found video: {file.get('name')} ({file.get('id')})")
                    video_ids.append({'id': file.get('id'), 'name': file.get('name'), 'path': current_path})

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    return video_ids

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download videos from a Google Drive folder.")
    parser.add_argument("folder_id", type=str, help="The Google Drive folder ID to scan for videos.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    args = parser.parse_args()

    target_folder_id = args.folder_id
    all_videos = get_video_ids_in_folder(target_folder_id, verbose=args.verbose)
    print(f"\nTotal videos found: {len(all_videos)}")

    for video in all_videos:
        output_dir = video['path']
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        full_output_path = os.path.join(output_dir, video['name'])
        print(f"\nStarting download for video: {full_output_path} ({video['id']})")
        gdrive_videoloader.main(video['id'], output_file=full_output_path, verbose=args.verbose)
